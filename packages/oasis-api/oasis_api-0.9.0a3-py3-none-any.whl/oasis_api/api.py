import serial
import socket
import time
import numpy as np
from datetime import datetime
import h5py

class OasisBoard:
    VOLTAGE_RANGE_ID = {
        2.5: 1,
        5: 2,
        6.25: 3,
        10: 4,
        12.5: 5,
    }
    ID_TO_VOLTAGE = {v: k for k, v in VOLTAGE_RANGE_ID.items()}
    PRETRIGGER_SAMPLES = 1000  # firmware constant
    CACHE_SIZE = 1500          # local cache for reading the serial port

    @staticmethod
    def bytes_to_array(data, n_samples, bytes_per_sample):
        return np.frombuffer(data, dtype=np.uint8).reshape(n_samples, bytes_per_sample).astype(int)

    def __init__(self, mode="serial", **kwargs):
        """
        mode: "serial", "tcp", or "offline"
        kwargs: 
            - serial: port, baudrate
            - tcp: ip, tcp_port
            - offline: no args
        """
        self.mode = mode
        self.ser = None
        self.sock = None
        self.connected = False
        self.OASISData = None
        self.t = None
        self._abort_requested = False
        self.verbose = kwargs.get("verbose", False)
        self._connection_args = kwargs
        # Parameters for sampling
        self.bits_per_sample = 18
        self.voltage_range = [5]*8
        self.t_sample = 1
        self.f_sample = 1000
        self.trigger_mode = False
        self.trigger_level = 0
        self.oversampling = 0
        self.sync_mode = 0
        # Decorator Handlers
        self._trigger_handlers = []

    def _vprint(self, msg):
        if self.verbose:
            print("[VERBOSE]", msg)

    def connect(self):
        if self.mode == "serial":
            return self.connect_serial(
                port=self._connection_args.get("port"),
                baudrate=self._connection_args.get("baudrate", 115200),
            )
        elif self.mode == "tcp":
            return self.connect_tcp(
                ip=self._connection_args.get("ip"),
                port=self._connection_args.get("tcp_port", 5025),
            )
        elif self.mode == "offline":
            self.connected = False
        else:
            raise ValueError(f"Unknown mode '{self.mode}'")

    def connect_serial(self, port, baudrate):
        if not port:
            raise ValueError("Serial port required for serial mode.")
        self.ser = serial.Serial(port=port, baudrate=baudrate, timeout=2, dsrdtr=True)
        self.ser.setDTR(True)
        self.ser.setRTS(False)
        self.connected = True
        self._vprint(f"Serial connected on {port} at {baudrate}")

    def connect_tcp(self, ip, port=5025):
        if not ip:
            raise ValueError("IP required for TCP mode.")
        self.sock = socket.create_connection((ip, port), timeout=5)
        self.sock.settimeout(5)
        self.connected = True
        self._vprint(f"TCP connected to {ip}:{port}")

    def close(self):
        if self.mode == "serial" and self.ser:
            self.ser.close()
            self.connected = False
        elif self.mode == "tcp" and self.sock:
            self.sock.close()
            self.connected = False

    def abort(self):
        self._abort_requested = True

    # --- Implementation of Decorator Pattern ---
    def on_trigger(self):
        """Decorator to register trigger event handlers."""
        def decorator(func):
            self._trigger_handlers.append(func)
            return func
        return decorator

    def _fire_trigger(self, *args, **kwargs):
        for handler in self._trigger_handlers:
            handler(*args, **kwargs)

    # --- Internal command dispatcher ---
    def _send_command(self, cmd, ack=None, timeout=5.0, collect_response=False, log=None):
        """
        Send a command and optionally wait for ack or collect full response.
        """
        if not self.connected and self.mode != "offline":
            self.connect()

        self._vprint(f"SEND: {cmd}")

        if self.mode == "serial":
            self.ser.write((cmd + "\n").encode("utf-8"))
            start = time.time()
            lines = []
            got_ack = False
            while True:
                if self.ser.inWaiting():
                    ans = self.ser.readline().decode("utf-8", errors="replace")
                    self._vprint(f"RECV: {ans.strip()}")
                    if log: log(ans.strip())
                    lines.append(ans)
                    if ack and ack in ans:
                        got_ack = True
                        if not collect_response:
                            return True
                        else:
                            break
                if ack is None and not collect_response:
                    return True
                if time.time() - start > timeout:
                    break
            if collect_response:
                return "".join(lines).strip()
            if ack and not got_ack:
                print(f"Timeout: No acknowledgment ('{ack}') from board for '{cmd}'")
            return got_ack

        elif self.mode == "tcp":
            self.sock.sendall((cmd + "\n").encode("utf-8"))
            start = time.time()
            lines = []
            got_ack = False
            buffer = b""
            while True:
                try:
                    ans = self.sock.recv(4096)
                    if not ans: break
                    buffer += ans
                    # TCP returns data, parse lines
                    while b"\n" in buffer:
                        line, buffer = buffer.split(b"\n", 1)
                        line_str = line.decode("utf-8", errors="replace")
                        self._vprint(f"RECV: {line_str.strip()}")
                        if log: log(line_str.strip())
                        lines.append(line_str)
                        if ack and ack in line_str:
                            got_ack = True
                            if not collect_response:
                                return True
                            else:
                                break
                    if ack and got_ack:
                        break
                except socket.timeout:
                    break
                if ack is None and not collect_response:
                    return True
                if time.time() - start > timeout:
                    break
            if collect_response:
                return "".join(lines).strip()
            if ack and not got_ack:
                print(f"Timeout: No acknowledgment ('{ack}') from board for '{cmd}'")
            return got_ack

        elif self.mode == "offline":
            raise RuntimeError("Cannot send command: offline mode.")

    def set_parameters(self, t_sample, f_sample, voltage_range, trigger=False, v_trigg=0, oversampling=0, sync_mode=0):
        self.t_sample = float(t_sample)
        self.f_sample = int(f_sample)
        self.voltage_range = np.array(voltage_range)
        self.trigger_mode = trigger
        self.trigger_level = float(v_trigg)
        self.oversampling = int(oversampling)
        self.sync_mode = int(sync_mode)
        if self.trigger_mode:
            n_points = self.PRETRIGGER_SAMPLES + int(self.t_sample * self.f_sample)
        else:
            n_points = int(self.t_sample * self.f_sample)
        self.OASISData = np.zeros([8, n_points])

    def write_parameters_to_device(self):
        if not self.connected:
            self.connect()
        voltage_ranges_ids = [self.VOLTAGE_RANGE_ID[float(v)] for v in self.voltage_range]
        params = [
            float(self.t_sample),
            float(self.f_sample),
            bool(self.trigger_mode),
            float(self.trigger_level),
            int(self.sync_mode),
            int(self.oversampling),
        ] + voltage_ranges_ids
        cmd = "OASIS.SetSamplingParams(" + ",".join(str(x) for x in params) + ")"
        ack = "[OASIS] OK"
        self._send_command(cmd, ack=ack)

    # === MAIN ACQUIRE DISPATCHER ===
    def acquire(self, print_log=None, progress=None, custom_filename=None, **kwargs):
        """
        Dispatch to mode-specific acquisition method.
        """
        if self.mode == "serial":
            return self.acquire_serial(print_log=print_log, progress=progress, custom_filename=custom_filename)
        elif self.mode == "tcp":
            return self.acquire_tcp(print_log=print_log, progress=progress, custom_filename=custom_filename, **kwargs)
        elif self.mode == "offline":
            raise RuntimeError("Cannot acquire data in offline mode.")
        else:
            raise ValueError(f"Unknown acquisition mode: {self.mode}")

    # === SERIAL ACQUISITION ===
    def acquire_serial(self, print_log=None, progress=None, custom_filename=None):
        def log(msg):
            if print_log: print_log(msg)
            else: print(msg)
        def emit_progress(value):
            if progress: progress(value)
        fileName = custom_filename or datetime.now().strftime("%Y-%m-%d-%H.%M.%S")
        if not self.connected:
            self.connect()

        # Set voltage ranges
        voltage_range_ids = []
        for v in self.voltage_range:
            try:
                voltage_range_ids.append(self.VOLTAGE_RANGE_ID[float(v)])
            except KeyError:
                raise ValueError(f"Invalid voltage range: {v}. Allowed: {list(self.VOLTAGE_RANGE_ID.keys())}")
        cmd = "OASIS.SetVoltageRange(" + ",".join(str(x) for x in voltage_range_ids) + ")"
        self._send_command(cmd, ack="[OASIS] OK", log=log)

        # Set oversampling
        cmd = f"OASIS.SetOversampling({self.oversampling})"
        self._send_command(cmd, ack="[OASIS] OK", log=log)

        # Start sampling
        V_TRIGG = self.trigger_level if self.trigger_mode else 0
        cmd = f"OASIS.Sample({self.t_sample},{self.f_sample},{V_TRIGG},{self.sync_mode},{fileName})"
        self._send_command(cmd, ack=None, log=log)

        # Data receive section
        total_samples = int(self.t_sample * self.f_sample)
        BYTES_PER_SAMPLE = 18
        BYTES_PER_CACHE = BYTES_PER_SAMPLE * self.CACHE_SIZE

        ser = self.ser
        while True:
            if self._abort_requested:
                self.close()
                log("Acquisition aborted.")
                raise RuntimeError("Aborted")
            if ser.inWaiting():
                SerialAnswer = ser.readline()
                if b"[OASIS] TRIGGERED" in SerialAnswer:
                    self._fire_trigger()
                if self.verbose and SerialAnswer != b"":
                    try:
                        print("[VERBOSE] RECV:", SerialAnswer.decode("utf-8", errors="replace").strip())
                    except Exception:
                        print("[VERBOSE] RECV: <binary data>", SerialAnswer)
                if SerialAnswer == b"<>\r\n":
                    break
                if SerialAnswer != b"":
                    log(SerialAnswer.decode("utf-8", errors="ignore"))
                if SerialAnswer in [
                    b"[OASIS] Sampling aborted.\r\n",
                    b"[OASIS] FATAL ERROR - Sampling too fast! Data processing did not finish in time.\r\n"
                ]:
                    log("Data Acquisition aborted.")
                    self.close()
                    raise RuntimeError("Aborted by device.")

        # Data transfer
        if self.trigger_mode:
            num_pre = self.PRETRIGGER_SAMPLES
            n_points = num_pre + total_samples
            OASISRcvBuffer = np.zeros([total_samples * BYTES_PER_SAMPLE], dtype=np.uint8)
        else:
            n_points = total_samples
            OASISRcvBuffer = np.zeros([total_samples * BYTES_PER_SAMPLE], dtype=np.uint8)

        # Read main data in cache chunks
        dataRcv = 0
        expected_bytes = int(total_samples / self.CACHE_SIZE) * BYTES_PER_CACHE
        while dataRcv != expected_bytes:
            if self._abort_requested:
                self.close()
                log("Acquisition aborted.")
                raise RuntimeError("Aborted")
            if ser.inWaiting():
                _OASISRcvBuffer = ser.read(BYTES_PER_CACHE)
                if self.verbose and _OASISRcvBuffer:
                    print(f"[VERBOSE] RECV (data-chunk): {len(_OASISRcvBuffer)} bytes")
                if len(_OASISRcvBuffer) != BYTES_PER_CACHE:
                    log("DEVICE ERROR! Serial communication timeout.")
                    self.close()
                    raise RuntimeError("Timeout")
                OASISRcvBuffer[dataRcv:dataRcv+BYTES_PER_CACHE] = np.frombuffer(_OASISRcvBuffer, dtype=np.uint8)
                dataRcv += BYTES_PER_CACHE
                emit_progress(int(dataRcv / expected_bytes * 100) if expected_bytes > 0 else 100)

        # Remainder
        remain_bytes = total_samples * BYTES_PER_SAMPLE - expected_bytes
        if remain_bytes > 0:
            _OASISRcvBuffer = ser.read(remain_bytes)
            if self.verbose and _OASISRcvBuffer:
                print(f"[VERBOSE] RECV (final): {len(_OASISRcvBuffer)} bytes")
            OASISRcvBuffer[dataRcv:dataRcv+remain_bytes] = np.frombuffer(_OASISRcvBuffer, dtype=np.uint8)

        if len(OASISRcvBuffer) == (total_samples * BYTES_PER_SAMPLE):
            emit_progress(100)
        else:
            log("DEVICE ERROR! Data lost.")
            self.close()
            raise RuntimeError("Data lost.")

        OASISDataRawMain = self.bytes_to_array(OASISRcvBuffer, total_samples, BYTES_PER_SAMPLE)

        # Pre-trigger (if used)
        if self.trigger_mode:
            time.sleep(1)
            self._send_command("Drq()", ack="<>\r\n", log=log)
            raw_pretrig = ser.read(BYTES_PER_SAMPLE * self.PRETRIGGER_SAMPLES)
            if self.verbose and raw_pretrig:
                print(f"[VERBOSE] RECV (pretrigger): {len(raw_pretrig)} bytes")
            OASISDataRawPreTrigg = self.bytes_to_array(raw_pretrig, self.PRETRIGGER_SAMPLES, BYTES_PER_SAMPLE)
            OASISDataRaw = np.concatenate((OASISDataRawPreTrigg, OASISDataRawMain))
        else:
            OASISDataRaw = OASISDataRawMain

        log("Data Acquisition finished.")
        self.decode_raw_data(OASISDataRaw)
        self.close()

    # === TCP ACQUISITION ===
    def acquire_tcp(self, print_log=None, progress=None, custom_filename=None, t_sample=None, f_sample=None,
                   voltage_range=None, trigger_level=None, sync_mode=None, oversampling=None, **kwargs):
        """
        Handles acquisition via TCP (SCPI style).
        Allows both default trigger (no params) and parametric requests.
        """
        def log(msg):
            if print_log:
                print_log(msg)
            else:
                print(msg)
        sock = self.sock
        if not self.connected:
            self.connect()

        # Build SCPI command string
        # If no custom params, just send "ACQ:SAMPLE?"
        if not any([custom_filename, t_sample, f_sample, voltage_range, trigger_level, sync_mode, oversampling]):
            cmd = "ACQ:SAMPLE?"
        else:
            # Compose parameter string
            params = []
            # Use the supplied or instance defaults
            params.append(str(float(t_sample if t_sample is not None else self.t_sample)))
            params.append(str(int(f_sample if f_sample is not None else self.f_sample)))
            params.append(str(float(trigger_level if trigger_level is not None else self.trigger_level)))
            params.append(str(int(sync_mode if sync_mode is not None else self.sync_mode)))
            params.append(str(int(oversampling if oversampling is not None else self.oversampling)))
            # Voltage ranges as list of int IDs
            vrange = voltage_range if voltage_range is not None else self.voltage_range
            vr = ','.join(str(self.VOLTAGE_RANGE_ID[float(v)]) for v in vrange)
            params.append(vr)
            # Optional filename
            if custom_filename:
                params.append(str(custom_filename))
            paramstr = ",".join(params)
            cmd = f"ACQ:SAMPLE?{paramstr}"

        sock.sendall((cmd + "\n").encode("utf-8"))
        log(f"Sent: {cmd}")

        # Wait for the "OASIS: Sampling..." header or error
        header = b''
        while True:
            chunk = sock.recv(1)
            if not chunk:
                raise RuntimeError("TCP connection closed by remote host.")
            header += chunk
            if header.endswith(b"\n"):
                line = header.decode("utf-8", errors="replace").strip()
                log(f"Recv: {line}")
                if line.startswith("ERR:"):
                    raise RuntimeError(line)
                elif "Sampling" in line:
                    break
                header = b''

        # Look for SCPI block header: #<numDigits><dataLen>
        block_header = b''
        while True:
            c = sock.recv(1)
            if not c:
                raise RuntimeError("TCP connection closed by remote host (data block)")
            if c == b'#':
                # Start of block
                len_digit = int(sock.recv(1).decode())
                len_str = sock.recv(len_digit).decode()
                data_len = int(len_str)
                # Now read data_len bytes:
                data_bytes = b""
                while len(data_bytes) < data_len:
                    more = sock.recv(data_len - len(data_bytes))
                    if not more:
                        break
                    data_bytes += more
                break
            block_header += c
            if block_header.endswith(b"ERR:"):
                err_msg = block_header + sock.recv(128)
                log(f"DEVICE ERROR: {err_msg.decode(errors='replace')}")
                raise RuntimeError(f"Device returned error: {err_msg}")

        # Optionally read trailing newline (not strictly needed)
        _ = sock.recv(1)

        # Decode data
        BYTES_PER_SAMPLE = 18
        n_samples = int(len(data_bytes) / BYTES_PER_SAMPLE)
        data_arr = self.bytes_to_array(data_bytes, n_samples, BYTES_PER_SAMPLE)
        self.decode_raw_data(data_arr)
        log("Data Acquisition finished.")
        self.close()

    def decode_raw_data(self, OASISRawData, voltage_range=None, bits_per_sample=None):
        if voltage_range is None:
            voltage_range = self.voltage_range
        if bits_per_sample is None:
            bits_per_sample = self.bits_per_sample

        num_samples, num_bytes = OASISRawData.shape   # shape: (num_samples, 18)
        BitDivider = 2 ** int(bits_per_sample) / 2

        # Vectorized bit extraction and accumulation
        OASISChannelData = np.zeros((num_samples, 8), dtype=np.int32)
        for n in range(8):
            bits = (OASISRawData & (1 << n)) >> n    # shape: (num_samples, 18)
            shifts = np.arange(17, -1, -1, dtype=np.int32)
            OASISChannelData[:, n] = np.dot(bits, 1 << shifts)

        # Now convert to voltages (vectorized)
        OASISChannelData = OASISChannelData.T    # shape: (8, num_samples)
        voltage_range = np.array(voltage_range)
        self.OASISData = np.where(
            OASISChannelData / BitDivider <= 1,
            (OASISChannelData * voltage_range[:, None]) / BitDivider,
            ((OASISChannelData - 2 * BitDivider) / BitDivider) * voltage_range[:, None]
        )

        # Time axis (unchanged)
        if self.trigger_mode:
            N = np.arange(-self.PRETRIGGER_SAMPLES + 1, int(self.t_sample * self.f_sample) + 1)
            self.t = N / self.f_sample
        else:
            self.t = np.arange(0, self.t_sample, 1 / self.f_sample)

    def save_data_h5(self, filename):
        num_ch, num_pts = self.OASISData.shape
        t = self.t
        channels = np.repeat(np.arange(1, num_ch+1), num_pts)
        times = np.tile(t, num_ch)
        voltages = self.OASISData.flatten()
        tidy = np.rec.fromarrays([channels, times, voltages], names=('channel', 'time', 'voltage'))
        with h5py.File(filename, 'w') as f:
            dset = f.create_dataset('data', data=tidy)
            dset.attrs['unit'] = 'V'
            f.attrs['duration_s'] = float(self.t_sample)
            f.attrs['sampling_frequency_hz'] = int(self.f_sample)
            f.attrs['voltage_ranges'] = np.array(self.voltage_range)
            f.attrs['unit'] = 'V'
            f.attrs['channels'] = num_ch
            f.attrs['format description'] = "Each row: [channel, time, voltage]"
        print(f"Saved tidy HDF5 data to {filename}")

    def save_data_mat(self, filename):
        savemat(filename, {
            **{f'OASISChannel{i+1}': self.OASISData[i] for i in range(8)},
            'OASISTime': self.t
        })

    def _parse_oasismeta(self, meta_path):
        with open(meta_path, "r") as f:
            content = f.read().strip()
        meta = {}
        # Split on ';', ignore empty fragments
        for fragment in content.split(';'):
            fragment = fragment.strip()
            if not fragment:
                continue
            if ',' in fragment:
                key, *vals = fragment.split(',')
                # For single-value keys: store as string; for multi: list of values
                if len(vals) == 1:
                    meta[key.strip()] = vals[0].strip()
                else:
                    meta[key.strip()] = [v.strip() for v in vals]
            else:
                meta[fragment.strip()] = None
        return meta

    def acquire_default(self):
        self._send_command("OASIS.Sample()", ack="[OASIS] OK")

    def mute_buzzer(self):
        self._send_command("OASIS.Mute()", ack="[OASIS] OK")

    def unmute_buzzer(self):
        self._send_command("OASIS.Unmute()", ack="[OASIS] OK")

    def enable_wifi(self):
        self._send_command("OASIS.EnableWiFi()", ack="[OASIS] OK")

    def disable_wifi(self):
        self._send_command("OASIS.DisableWiFi()", ack="[OASIS] OK")

    def device_info(self):
        return self._send_command("OASIS.Info()", collect_response=True)

    def device_raw_info(self):
        return self._send_command("OASIS.RawInfo()", collect_response=True)

    def set_device_info(self):
        return self._send_command("OASIS.SetDeviceInfo()", collect_response=True)

    def load_from_files(self, meta_path, raw_path=None, pretrig_raw_path=None, print_log=None):
        """
        Loads and decodes OASIS SD-card files (.OASISmeta, .OASISraw, and optional pretrigger raw).
        Populates self.OASISData and self.t just as if acquired.
        """
        def log(msg):
            if print_log:
                print_log(msg)
            else:
                print(msg)

        meta = self._parse_oasismeta(meta_path)
        log(f"Meta parsed: {meta}")

        # Required parameter handling (support for single values and list)
        def get1(key, default=None, as_type=str):
            v = meta.get(key, default)
            if v is None:
                if default is not None:
                    return as_type(default)
                raise ValueError(f"Meta file missing required key '{key}'")
            if isinstance(v, list):
                v = v[0]
            return as_type(v)

        # Now get required values:
        adc_bits = get1('ADC_BITS', 18, int)
        n_sample = get1('n_sample', None, int)
        self.f_sample = get1('f_sample', None, float)
        self.t_sample = get1('t_sample', None, float)
        self.trigger_level = float(meta.get('trigger_level', 0))
        self.trigger_mode = self.trigger_level != 0
        voltage_range = meta.get('VoltageRanges', None)
        if voltage_range is None:
            raise ValueError("Missing 'VoltageRanges' in meta.")
        if isinstance(voltage_range, list):
            self.voltage_range = [float(v) for v in voltage_range]
        else:
            self.voltage_range = [float(x) for x in voltage_range.split(',')]

        # 3. Load main raw
        if raw_path is None:
            raw_path = meta_path.replace(".OASISmeta", ".OASISraw")
        with open(raw_path, "rb") as f:
            OASISRawData = f.read()
        # 4. Optionally load pretrigger
        if self.trigger_mode:
            if pretrig_raw_path is None:
                pretrig_raw_path = meta_path.replace(".OASISmeta", "_PRE.OASISraw")
            with open(pretrig_raw_path, "rb") as f:
                OASISRawPre = f.read()
            OASISRawData = OASISRawPre + OASISRawData

        # 5. Reshape and decode
        n_samples = int(len(OASISRawData) / 18)
        data_arr = self.bytes_to_array(OASISRawData, n_samples, 18)
        self.decode_raw_data(data_arr, voltage_range=self.voltage_range, bits_per_sample=adc_bits)

        if self.trigger_mode:
            N = np.arange(-self.PRETRIGGER_SAMPLES + 1, n_samples-self.PRETRIGGER_SAMPLES + 1)
            self.t = N / self.f_sample
        else:
            self.t = np.arange(0, self.t_sample, 1 / self.f_sample)

        log(f"[OASIS-TUI]: Decoded {n_samples} samples from SD card raw data.")

    def plot_data(self):
        import matplotlib.pyplot as plt
        fig, axs = plt.subplots(4, 2, figsize=(14, 10))
        axs = axs.flatten()
        for k in range(8):
            axs[k].plot(self.t, self.OASISData[k])
            axs[k].set_title(f"Channel {k+1}")
            axs[k].set_xlabel("Time [s]")
            axs[k].set_ylabel("Voltage [V]")
            v = abs(self.voltage_range[k])
            axs[k].set_ylim(-v, v)
            if self.trigger_mode:
                axs[k].axvline(0, color='red', linestyle='--', label='Trigger')
        plt.tight_layout()
        plt.show()
