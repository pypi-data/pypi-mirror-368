class Motor:
    def __init__(self):
        self.module_registers = {
            "high_bit_mac_address": 1,
            "low_bit_mac_address": 2,
            "ip": 3,
            "netmask": 4,
            "gateway": 5,
            "setup_bits": 6,
            "outputs": 7,
            "poll_factor": 8,
            "station_alias": 9,
            "modbus_timeout": 10,
            "input_mask": 11,
            "default_homing": 12,
            "reset_delay": 13,
            "command": 15,
            "cyclic_read_1": 16,
            "cyclic_read_2": 17,
            "cyclic_read_3": 18,
            "cyclic_read_4": 19,
            "cyclic_read_5": 20,
            "cyclic_read_6": 21,
            "cyclic_read_7": 22,
            "cyclic_read_8": 23,
            "cyclic_write_1": 24,
            "cyclic_write_2": 25,
            "cyclic_write_3": 26,
            "cyclic_write_4": 27,
            "cyclic_write_5": 28,
            "cyclic_write_6": 29,
            "cyclic_write_7": 30,
            "cyclic_write_8": 31,
            "serial_no": 32,
            "hardware_version": 33,
            "software_version": 34,
            "n_internal_com_timeout": 35,
            "n_retry_frames": 36,
            "n_discarded_frames": 37,
            "total_frames": 38,
            "n_spi_crc_err": 39,
            "n_sync_incidences": 40,
            "inputs": 47,
            "status_bits": 48,
            "installed_protocol": 49
        }

        self.module_setup_bits = {
            "err_handling": 0,
            "disable_err_handling": 1,
            "clear_station_name": 2,
            "enable_drive_profile": 3,
            "endless_relative": 4,
            "mirror_registers": 5,
            "pdo_8": 6,
            "input_de_bounce": 7,
            "output_mirror": 8,
            "input_mirror": 9,
            "dhcp_enable": 10,
            "cia402_units": 11,
            "swap_databytes": 12,
            "cycle_setup": 13
        }

        self.module_cmd_register = {
            "reset": 1,
            "reset_delay": 2,
            "save2flash": 16,
            "restore_factory_default": 18,
            "copy_sync0_out1": 19,
            "remove_sync0_out1": 20,
            "reinit_cyclic": 21,
            "disable_cyclic_write": 22,
            "reenable_cyclic_write": 23,
            "reinit_internal_com": 25,
            "reset_motor_module": 257,
            "reset_motor_module_delay": 258,
            "reset_motor_delay": 259,
            "save2flash_motor_resync": 272,
            "save2flash_motor": 273
        }

        self.module_status_bits = {
            "no_motor_com": 7,
            "cyclic_running": 9,
            "dc_enable": 10,
            "udp_mactalk": 11,
            "rs232_mactalk": 12,
            "sync_error": 13,
            "nl_error": 14,
            "pl_error": 15,
            "spi_internal_com": 16,
            "old_firmware": 17,
            "cyclic_blocked": 18
        }

        self.module_protocol = {
            "EthernetIP": 0x34,
            "EtherCAT": 0x35,
            "EthernetPowerLink": 0x36,
            "ProfiNet": 0x37,
            "ModbusTCP": 0x38,
            "SercoIII": 0x39
        }