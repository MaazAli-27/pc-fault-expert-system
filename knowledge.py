"""Knowledge base: 138 IF-THEN rules + input field definitions + sample scenarios."""
from engine import Rule
T, F = True, False
def R(i, c, conds, concl, cf, prio, sev, atype="", cost="", action=""):
    return Rule(i, c, conds, concl, cf, prio, sev, atype, cost, action)
f_ = lambda n: "fault:" + n
RULES = [
# ---- Power & Boot (8)
R("P01","Power",{"no_power":T,"fans_spin":F,"power_cable_loose":F},f_("psu_failure"),.85,9,4,"Replace","Medium","Test with a known-good PSU; replace the power supply if the PC stays dead."),
R("P02","Power",{"no_power":T,"power_cable_loose":T},f_("loose_power_cable"),.95,9,2,"Repair","Free","Reseat the power cable and check the wall socket/power strip."),
R("P03","Power",{"psu_smell":T},f_("psu_failure"),.95,10,4,"Replace","Medium","Unplug immediately and replace the PSU; check other parts for damage."),
R("P04","Power",{"fans_spin":T,"post_ok":F,"beeps":F},f_("motherboard_failure"),.6,6,4,"Further Test","High","Test with minimal components; if still no POST, repair or replace the motherboard."),
R("P05","Power",{"clock_reset":T},f_("cmos_battery_dead"),.9,5,1,"Replace","Low","Replace the CR2032 CMOS battery on the motherboard."),
R("P06","Power",{"beeps":T,"fans_spin":T,"post_ok":F},f_("ram_seating_problem"),.7,6,2,"Repair","Free","Reseat RAM sticks and clean the contacts; test one stick at a time."),
R("P07","Power",{"no_boot_device":T,"bios_sees_drive":F},f_("storage_connection_failure"),.75,7,3,"Repair","Low","Check SATA/NVMe cables and seating; try another port or cable."),
R("P08","Power",{"power_intermittent":T,"power_cable_loose":F},f_("psu_degraded"),.65,7,3,"Further Test","Medium","Test with a spare PSU and a power-supply tester."),
# ---- RAM (6)
R("M01","RAM",{"beeps":T,"bsod":T},f_("faulty_ram"),.9,8,3,"Replace","Low","Run MemTest86, then replace the failing RAM stick."),
R("M02","RAM",{"ram_errors":T},f_("faulty_ram"),.95,9,3,"Replace","Low","Replace the RAM stick that fails MemTest86."),
R("M03","RAM",{"ram_new_unstable":T,"bsod":T},f_("incompatible_ram"),.8,7,3,"Replace","Low","Remove the new RAM or replace it with modules matching the motherboard spec."),
R("M04","RAM",{"mem_grows":T,"slow":T},f_("memory_leak_software"),.8,5,2,"Update","Free","Identify the leaking process in Task Manager; update or reinstall it."),
R("M05","RAM",{"mem_usage_high":T,"mem_grows":F,"slow":T},f_("insufficient_ram"),.7,4,2,"Upgrade","Low","Add more RAM or close memory-heavy applications."),
R("M06","RAM",{"bsod":T,"ram_errors":F,"beeps":F},f_("ram_suspected"),.4,3,2,"Further Test","Free","Run Windows Memory Diagnostic or MemTest86 to rule out RAM."),
# ---- CPU & Thermal (8)
R("C01","CPU",{"cpu_temp":"high","random_shutdown":T},"d:thermal_shutdown",1.0,8,0),
R("C02","CPU",{"d:thermal_shutdown":T,"fan_spinning":F},f_("cpu_fan_failure"),.9,9,3,"Replace","Low","Replace the CPU fan/cooler and avoid using the PC until then."),
R("C03","CPU",{"d:thermal_shutdown":T,"fan_spinning":T,"pc_old":T},f_("dried_thermal_paste"),.8,6,2,"Repair","Low","Clean the CPU and apply fresh thermal paste."),
R("C04","CPU",{"cpu_temp":"high","fan_noisy":T,"dust":T},f_("dust_buildup"),.85,6,2,"Clean","Free","Clean fans, heatsink and vents with compressed air."),
R("C05","CPU",{"cpu_temp":"high","slow":T},"d:thermal_throttling",1.0,7,0),
R("C06","CPU",{"d:thermal_throttling":T},f_("cpu_overheating"),.8,6,3,"Clean","Free","Clean dust, check fan speed, improve airflow, re-paste if old."),
R("C07","CPU",{f_("cpu_fan_failure"):T},"d:cooling_failure",1.0,8,0),
R("C08","CPU",{"d:cooling_failure":T},f_("cpu_overheating_risk"),.9,8,4,"Replace","Low","Do not run the PC under load; the CPU can be permanently damaged."),
# ---- Storage (8)
R("S01","Storage",{"hdd_clicking":T,"smart_status":"failing"},f_("hdd_mechanical_failure"),.95,10,4,"Replace","Medium","Back up data immediately, then replace the hard drive."),
R("S02","Storage",{"hdd_clicking":T,"smart_status":"ok"},f_("hdd_early_failure"),.6,8,3,"Further Test","Free","Back up data now and run the manufacturer's drive diagnostic."),
R("S03","Storage",{"smart_status":"failing","drive_type":"ssd"},f_("ssd_failing"),.9,9,4,"Replace","Medium","Back up data and replace the SSD under warranty if possible."),
R("S04","Storage",{"bad_sectors":T,"drive_type":"hdd"},f_("hdd_bad_sectors"),.85,8,3,"Repair","Free","Back up, run chkdsk /r; replace the drive if bad sectors grow."),
R("S05","Storage",{"ssd_wear_high":T,"drive_type":"ssd"},f_("ssd_wear"),.8,6,3,"Replace","Medium","Plan an SSD replacement and keep regular backups."),
R("S06","Storage",{"free_space_low":T,"disk_usage_100":T},f_("disk_full_issue"),.85,5,2,"Clean","Free","Run Disk Cleanup, remove large files, uninstall unused programs."),
R("S07","Storage",{"fs_errors":T},f_("corrupt_file_system"),.8,7,3,"Repair","Free","Run chkdsk /f from recovery media after backing up data."),
R("S08","Storage",{"disk_usage_100":T,"free_space_low":F,"slow":T},f_("software_disk_load"),.7,4,2,"Scan","Free","Check Task Manager for the process using the disk; scan for malware, disable indexing/updates."),
# ---- GPU & Display (5)
R("G01","GPU",{"artifacts":T,"gpu_temp":"high"},f_("gpu_overheating"),.85,8,3,"Clean","Free","Clean the GPU fans, improve airflow, replace GPU paste if needed."),
R("G02","GPU",{"artifacts":T,"gpu_temp":"normal","games_only":F},f_("gpu_failure"),.8,7,3,"Replace","High","Test the card in another PC; replace it if artifacts remain."),
R("G03","GPU",{"display_driver_crash":T},f_("gpu_driver_crash"),.85,6,2,"Update","Free","Clean-install the latest GPU driver (use DDU)."),
R("G04","GPU",{"no_display":T,"fans_spin":T,"display_cable_loose":T},f_("loose_display_cable"),.9,7,1,"Repair","Free","Reseat the HDMI/DisplayPort cable at both ends."),
R("G05","GPU",{"artifacts":T,"gpu_temp":"normal","games_only":T},f_("game_or_gpu_driver_issue"),.6,5,2,"Update","Free","Update GPU drivers and verify the game files."),
# ---- Network (6)
R("N01","Network",{"no_internet":T,"other_devices_ok":T,"wifi_adapter_missing":T},f_("faulty_nic"),.8,7,3,"Replace","Low","Replace the network card or use a USB adapter."),
R("N02","Network",{"no_internet":T,"other_devices_ok":T,"wifi_adapter_missing":F,"driver_outdated":T},f_("nic_driver_issue"),.8,6,2,"Update","Free","Update or reinstall the network adapter driver."),
R("N03","Network",{"no_internet":T,"other_devices_ok":F},f_("router_or_isp_fault"),.85,6,2,"Repair","Free","Power-cycle the router/modem; contact the ISP if it persists."),
R("N04","Network",{"dns_fail":T},f_("dns_issue"),.9,5,1,"Repair","Free","Flush DNS and switch to 8.8.8.8 / 1.1.1.1."),
R("N05","Network",{"ip_conflict":T},f_("ip_address_conflict"),.9,5,1,"Repair","Free","Release/renew the IP and use DHCP; remove duplicate static IPs."),
R("N06","Network",{"no_internet":T,"other_devices_ok":T,"wifi_adapter_missing":F,"driver_outdated":F,"ip_conflict":F,"dns_fail":F},f_("network_stack_corrupt"),.5,3,2,"Repair","Free","Run 'netsh winsock reset' and 'netsh int ip reset', then reboot."),
# ---- Operating System (7)
R("O01","OS",{"boot_loop":T,"update_recent":T},f_("failed_os_update"),.9,8,3,"Repair","Free","Boot to recovery and uninstall the latest update or use System Restore."),
R("O02","OS",{"bsod":T,"sys_files_corrupt":T},f_("corrupt_system_files"),.85,7,3,"Repair","Free","Run sfc /scannow and DISM /RestoreHealth."),
R("O03","OS",{"bootloader_missing":T},f_("boot_loader_damage"),.9,8,3,"Repair","Free","Use recovery media: bootrec /fixmbr /fixboot /rebuildbcd."),
R("O04","OS",{"sys_files_corrupt":T,"fs_errors":T,"bsod":T},f_("os_reinstall_needed"),.85,6,3,"Reinstall","Medium","Back up files and reinstall the operating system."),
R("O05","OS",{"bsod":T,"driver_recent_install":T},f_("bsod_driver_conflict"),.8,7,2,"Update","Free","Roll back or update the recently installed driver in Safe Mode."),
R("O06","OS",{"bsod":T,"update_recent":T},f_("bsod_after_update"),.7,6,2,"Repair","Free","Uninstall the latest update or restore to an earlier restore point."),
R("O07","OS",{"slow":T,"os_old_install":T,"sys_files_corrupt":F,"startup_many":F,"unknown_programs":F,"disk_usage_100":F},f_("aging_os_installation"),.5,2,1,"Reinstall","Medium","Consider a clean OS reinstall after backing up files."),
# ---- Malware & Security (5)
R("X01","Security",{"pop_ups":T,"unknown_programs":T},f_("malware_infection"),.9,8,3,"Scan","Free","Boot Safe Mode, run a full antivirus + Malwarebytes scan, remove unknown programs."),
R("X02","Security",{"browser_hijacked":T},f_("adware_browser_hijack"),.85,6,2,"Scan","Free","Remove suspicious extensions, reset the browser, run an adware scan."),
R("X03","Security",{"files_encrypted":T},f_("ransomware"),.98,10,4,"Further Test","High","Disconnect from the network, do not pay, restore from clean backups, report it."),
R("X04","Security",{"av_disabled":T,"high_cpu_idle":T},f_("malware_infection"),.8,8,3,"Scan","Free","Re-enable antivirus, run an offline scan."),
R("X05","Security",{"high_cpu_idle":T,"unknown_programs":T,"pop_ups":F},f_("cryptominer_suspected"),.6,5,3,"Scan","Free","Check processes for unknown high-CPU tasks and scan."),
# ---- Drivers & Software (5)
R("D01","Software",{"driver_outdated":T,"device_malfunction":T},f_("outdated_driver"),.75,5,2,"Update","Free","Update the device driver from the manufacturer's site."),
R("D02","Software",{"app_crash_specific":T,"driver_outdated":F},f_("app_corrupt_or_conflict"),.7,4,1,"Reinstall","Free","Repair or reinstall the application; check for conflicting software."),
R("D03","Software",{"startup_many":T,"slow":T},f_("startup_overload"),.8,3,1,"Clean","Free","Disable unneeded startup programs in Task Manager."),
R("D04","Software",{"registry_errors":T},f_("registry_issue"),.6,3,2,"Repair","Free","Run sfc /scannow and restore from a restore point; avoid registry cleaners."),
R("D05","Software",{"app_crash_specific":T,"driver_outdated":T},f_("driver_app_conflict"),.65,5,2,"Update","Free","Update drivers (especially GPU/audio) and the application."),
# ---- Peripherals (3)
R("H01","Peripherals",{"usb_dead_all":T},f_("usb_controller_or_driver"),.7,5,2,"Update","Free","Reinstall USB controller drivers; check BIOS USB settings."),
R("H02","Peripherals",{"usb_dead_one":T,"usb_dead_all":F},f_("usb_port_failure"),.8,4,1,"Repair","Low","Use another port; repair the port if it is physically damaged."),
R("H03","Peripherals",{"kb_mouse_fail":T,"usb_dead_all":F},f_("peripheral_failure"),.8,4,1,"Replace","Low","Test on another PC; replace the keyboard/mouse or batteries."),
# ---- Derived (chaining)
R("D06","Derived",{"smart_status":"failing"},"d:data_at_risk",1.0,9,0),
R("D07","Derived",{"d:data_at_risk":T},f_("backup_urgent"),.99,10,4,"Further Test","Free","Back up all important data NOW before any other repair."),
]
assert len({r.id for r in RULES}) == len(RULES) >= 50

# (group, key, label, options|None)
FIELDS = [
("Power & Boot","no_power","PC does not power on at all",None),("Power & Boot","fans_spin","Fans spin when powered",None),
("Power & Boot","power_cable_loose","Power cable loose/unplugged",None),("Power & Boot","psu_smell","Burning smell from PC",None),
("Power & Boot","power_intermittent","Powers on only intermittently",None),("Power & Boot","clock_reset","Date/time resets",None),
("Power & Boot","beeps","Beep codes at startup",None),("Power & Boot","post_ok","Reaches BIOS/POST screen",None),
("Power & Boot","no_boot_device","'No boot device' message",None),("Power & Boot","bios_sees_drive","BIOS detects the drive",None),
("Power & Boot","bootloader_missing","Boot loader/BCD missing error",None),("Power & Boot","boot_loop","Restarts in a boot loop",None),
("RAM","bsod","Blue screens (BSOD)",None),("RAM","ram_errors","MemTest86 reports errors",None),
("RAM","ram_new_unstable","Unstable after adding new RAM",None),("RAM","mem_usage_high","Memory usage constantly high",None),
("RAM","mem_grows","Memory usage keeps growing over time",None),
("CPU & Thermal","cpu_temp","CPU temperature",["normal","high"]),("CPU & Thermal","random_shutdown","Random shutdowns",None),
("CPU & Thermal","fan_spinning","CPU fan spinning",None),("CPU & Thermal","fan_noisy","Fans very loud",None),
("CPU & Thermal","dust","Visible dust inside",None),("CPU & Thermal","pc_old","PC older than 3 years",None),
("CPU & Thermal","slow","PC is slow / lagging",None),
("Storage","drive_type","Drive type",["ssd","hdd"]),("Storage","hdd_clicking","Drive makes clicking noises",None),
("Storage","smart_status","SMART status",["ok","failing"]),("Storage","bad_sectors","Bad sectors found",None),
("Storage","disk_usage_100","Disk usage at 100%",None),("Storage","free_space_low","Free space below 10%",None),
("Storage","ssd_wear_high","SSD wear level high",None),("Storage","fs_errors","File system errors",None),
("Display","artifacts","Screen artifacts / glitches",None),("Display","gpu_temp","GPU temperature",["normal","high"]),
("Display","games_only","Artifacts only in games",None),("Display","display_driver_crash","'Display driver stopped responding'",None),
("Display","no_display","No display signal",None),("Display","display_cable_loose","Display cable loose",None),
("Network","no_internet","This device has no internet",None),("Network","other_devices_ok","Other devices get internet",None),
("Network","wifi_adapter_missing","Network adapter missing in OS",None),("Network","dns_fail","Websites fail but pinging an IP works",None),
("Network","ip_conflict","IP address conflict message",None),
("Operating System","update_recent","Problem began after an update",None),("Operating System","sys_files_corrupt","Corrupt system files (SFC)",None),
("Operating System","driver_recent_install","Problem began after a driver install",None),("Operating System","os_old_install","OS installed 2+ years ago",None),
("Security","pop_ups","Pop-ups appear",None),("Security","unknown_programs","Unknown programs installed",None),
("Security","browser_hijacked","Browser homepage/search changed",None),("Security","files_encrypted","Files encrypted / ransom note",None),
("Security","av_disabled","Antivirus disabled by itself",None),("Security","high_cpu_idle","High CPU while idle",None),
("Software & Peripherals","driver_outdated","Outdated drivers",None),("Software & Peripherals","device_malfunction","A device malfunctions",None),
("Software & Peripherals","app_crash_specific","One specific app crashes",None),("Software & Peripherals","startup_many","Many startup programs",None),
("Software & Peripherals","registry_errors","Registry errors",None),("Software & Peripherals","usb_dead_one","One USB port dead",None),
("Software & Peripherals","usb_dead_all","All USB ports dead",None),("Software & Peripherals","kb_mouse_fail","Keyboard/mouse not working",None),
]

SAMPLES = {
 "1. Won't power on": {"no_power":T,"fans_spin":F},
 "2. Random shutdowns + hot CPU": {"cpu_temp":"high","random_shutdown":T,"fan_spinning":F},
 "3. Clicking HDD + SMART warning": {"drive_type":"hdd","hdd_clicking":T,"smart_status":"failing","slow":T},
 "4. Beeps + BSODs": {"beeps":T,"bsod":T,"post_ok":F},
 "5. Pop-ups + unknown programs": {"pop_ups":T,"unknown_programs":T,"slow":T},
 "6. One device offline": {"no_internet":T,"wifi_adapter_missing":T},
 "7. Boot loop after update": {"boot_loop":T,"update_recent":T},
 "8. Artifacts in games, hot GPU": {"artifacts":T,"games_only":T,"gpu_temp":"high"},
 "9. Disk 100% + low space": {"disk_usage_100":T,"free_space_low":T,"slow":T},
 "10. Multiple faults": {"cpu_temp":"high","slow":T,"dust":T,"fan_noisy":T,"pop_ups":T,"unknown_programs":T,"free_space_low":T,"disk_usage_100":T},
 "11. Bluetooth headphones won't connect": {"bt_pairs_no_connect":T,"bt_works_other":"yes"},
 "12. Wi-Fi connected but no internet": {"wifi_connected_no_internet":T,"other_devices_ok":T,"dns_fail":T},
}


# ---- extended knowledge base (47 more rules, 17 more symptom fields)
EXTRA_FIELDS = [
("Power & Boot","laptop_not_charging","Laptop not charging",None),("Power & Boot","battery_drains","Battery drains very quickly",None),
("Power & Boot","swollen_battery","Battery looks swollen/bulging",None),("Power & Boot","stuck_logo","Stuck at the manufacturer logo",None),
("RAM","freezes","PC freezes randomly",None),
("CPU & Thermal","hot_at_idle","PC hot even when idle",None),("CPU & Thermal","overclocked","CPU/RAM is overclocked",None),
("CPU & Thermal","runaway_process","One program uses very high CPU",None),
("Storage","external_drive_fail","External drive/flash drive not detected",None),
("Display","screen_cracked","Screen physically cracked",None),("Display","wrong_resolution","Wrong/stretched screen resolution",None),
("Network","wifi_drops","Wi-Fi keeps disconnecting",None),("Network","slow_internet","Internet is very slow",None),
("Operating System","login_fail","Cannot log in / profile error",None),("Operating System","update_stuck","Updates are stuck or fail to install",None),
("Security","email_spam","Contacts get spam from my email / account hacked",None),
("Software & Peripherals","no_sound","No sound/audio",None),
]
EXTRA_RULES = [
# Laptop / power (6)
R("L01","Power",{"laptop_not_charging":T,"power_cable_loose":F},f_("faulty_charger_or_port"),.7,6,2,"Replace","Low","Test with another charger; inspect the charging port."),
R("L02","Power",{"laptop_not_charging":T,"battery_drains":T},f_("battery_worn"),.8,6,2,"Replace","Low","Replace the worn battery."),
R("L03","Power",{"battery_drains":T,"pc_old":T},f_("battery_worn"),.75,5,2,"Replace","Low","Replace the battery; check battery health report (powercfg /batteryreport)."),
R("L04","Power",{"swollen_battery":T},f_("swollen_battery_hazard"),.98,10,4,"Replace","Low","Stop using and unplug immediately; have the battery replaced safely. Fire risk."),
R("L05","Power",{"stuck_logo":T,"clock_reset":T},f_("bios_settings_reset"),.7,6,2,"Repair","Free","Load BIOS defaults, check boot order, replace the CMOS battery."),
R("L06","Power",{"stuck_logo":T,"bootloader_missing":F,"no_boot_device":F},f_("bios_boot_config_issue"),.55,4,2,"Repair","Free","Check BIOS boot mode/order (UEFI vs Legacy) and reset BIOS defaults."),
# Freezes / CPU / RAM (10)
R("F01","RAM",{"freezes":T,"ram_errors":T},f_("faulty_ram"),.85,8,3,"Replace","Low","Replace the RAM stick that fails MemTest86."),
R("F02","CPU",{"freezes":T,"cpu_temp":"high"},f_("cpu_overheating"),.8,7,3,"Clean","Free","Clean dust, check fan speed, re-paste the CPU."),
R("F03","Storage",{"freezes":T,"smart_status":"failing"},f_("storage_failure_freezing"),.8,8,4,"Replace","Medium","Back up data and replace the failing drive."),
R("F04","Power",{"freezes":T,"random_shutdown":T,"cpu_temp":"normal"},f_("psu_degraded"),.6,6,3,"Further Test","Medium","Test with a spare PSU; power instability causes freezes and shutdowns."),
R("F05","CPU",{"overclocked":T,"bsod":T},f_("unstable_overclock"),.9,8,2,"Repair","Free","Reset BIOS to default speeds/voltages."),
R("F06","CPU",{"overclocked":T,"random_shutdown":T},f_("unstable_overclock"),.8,7,2,"Repair","Free","Reset BIOS to defaults and test stability."),
R("F07","CPU",{"hot_at_idle":T,"dust":F,"pc_old":T},f_("dried_thermal_paste"),.8,6,2,"Repair","Low","Replace the CPU thermal paste."),
R("F08","CPU",{"hot_at_idle":T,"fan_spinning":T,"pc_old":F},f_("cooler_not_seated"),.6,5,2,"Repair","Free","Reseat the CPU cooler and check mounting pressure."),
R("F09","CPU",{"runaway_process":T,"high_cpu_idle":F},f_("runaway_process_issue"),.8,5,2,"Repair","Free","End the process, then update or reinstall the application."),
R("F10","CPU",{"hot_at_idle":T,"high_cpu_idle":T},f_("background_process_load"),.7,5,2,"Scan","Free","Find the background process in Task Manager; scan for malware."),
# Storage (5)
R("T01","Storage",{"external_drive_fail":T,"usb_dead_all":F,"usb_dead_one":F},f_("external_drive_fault"),.75,5,2,"Replace","Low","Test the cable/another PC; replace the drive or cable."),
R("T02","Storage",{"external_drive_fail":T,"usb_dead_one":T},f_("usb_port_failure"),.8,5,1,"Repair","Free","Use a different USB port; repair the damaged port."),
R("T03","Storage",{"free_space_low":T,"slow":T,"disk_usage_100":F},f_("low_space_slowdown"),.6,3,1,"Clean","Free","Free up at least 15% of the drive; remove temp files."),
R("T04","Storage",{"smart_status":"failing","bad_sectors":T},f_("drive_end_of_life"),.95,10,4,"Replace","Medium","Drive is at end of life: back up now and replace."),
R("T05","Storage",{"ssd_wear_high":T,"slow":T},f_("ssd_performance_degraded"),.7,5,2,"Upgrade","Medium","Replace/upgrade the SSD; keep it under 80% full."),
# Display (5)
R("V01","Display",{"screen_cracked":T},f_("broken_screen"),.95,7,3,"Replace","High","Replace the display panel."),
R("V02","Display",{"wrong_resolution":T,"driver_outdated":T},f_("display_driver_missing"),.8,6,2,"Update","Free","Install the correct GPU driver from the manufacturer."),
R("V03","Display",{"artifacts":T,"display_cable_loose":T,"no_display":F},f_("loose_display_cable"),.85,7,1,"Repair","Free","Reseat or replace the HDMI/DisplayPort cable."),
R("V04","Display",{"no_display":T,"fans_spin":T,"post_ok":T,"display_cable_loose":F},f_("monitor_or_cable_failure"),.55,5,2,"Further Test","Free","Try another monitor, cable and port."),
R("V05","Display",{"artifacts":T,"gpu_temp":"normal","display_driver_crash":T},f_("gpu_driver_crash"),.9,7,2,"Update","Free","Clean-install the GPU driver (DDU)."),
# Network (5)
R("W01","Network",{"wifi_drops":T,"other_devices_ok":T},f_("wifi_adapter_or_driver"),.7,6,2,"Update","Free","Update the Wi-Fi driver; disable adapter power saving."),
R("W02","Network",{"wifi_drops":T,"other_devices_ok":F},f_("router_unstable"),.7,6,2,"Repair","Free","Restart/update the router; change Wi-Fi channel."),
R("W03","Network",{"slow_internet":T,"other_devices_ok":F},f_("isp_or_router_issue"),.6,5,2,"Further Test","Free","Run a speed test on the router; contact your ISP."),
R("W04","Network",{"slow_internet":T,"other_devices_ok":T,"pop_ups":T},f_("malware_infection"),.8,7,3,"Scan","Free","Run a full malware scan; slow internet plus pop-ups suggests adware."),
R("W05","Network",{"slow_internet":T,"other_devices_ok":T,"driver_outdated":T},f_("nic_driver_issue"),.7,5,2,"Update","Free","Update the network adapter driver."),
# OS (6)
R("Y01","OS",{"login_fail":T},f_("corrupt_user_profile"),.8,6,2,"Repair","Free","Create a new user profile and copy data across."),
R("Y02","OS",{"update_stuck":T},f_("update_service_corrupt"),.8,5,2,"Repair","Free","Run the Windows Update troubleshooter and reset update components."),
R("Y03","OS",{"update_stuck":T,"free_space_low":T},f_("disk_full_issue"),.75,6,2,"Clean","Free","Free disk space; updates need several GB."),
R("Y04","OS",{"boot_loop":T,"update_recent":F,"sys_files_corrupt":T},f_("corrupt_system_files"),.8,7,3,"Repair","Free","Run startup repair, then sfc /scannow and DISM from recovery."),
R("Y05","OS",{"boot_loop":T,"bsod":T,"driver_recent_install":T},f_("bsod_driver_conflict"),.85,8,3,"Update","Free","Boot Safe Mode and roll back the new driver."),
R("Y06","OS",{"stuck_logo":T,"update_recent":T},f_("failed_os_update"),.7,6,3,"Repair","Free","Wait for the update to finish; if stuck, use recovery to remove it."),
# Security (4)
R("Z01","Security",{"email_spam":T},f_("account_compromised"),.85,8,3,"Repair","Free","Change passwords from a clean device, enable 2FA, scan this PC."),
R("Z02","Security",{"pop_ups":F,"browser_hijacked":T,"unknown_programs":T},f_("malware_infection"),.85,8,3,"Scan","Free","Uninstall unknown programs and run a full malware scan."),
R("Z03","Security",{"files_encrypted":T,"av_disabled":T},f_("ransomware"),.99,10,4,"Further Test","High","Disconnect from network, do not pay, restore from clean backups."),
R("Z04","Security",{"high_cpu_idle":T,"fan_noisy":T,"unknown_programs":T},f_("cryptominer_suspected"),.75,6,3,"Scan","Free","Check processes and scan for cryptominers."),
# Software & peripherals (6)
R("A01","Software",{"no_sound":T,"driver_outdated":T},f_("audio_driver_issue"),.8,5,1,"Update","Free","Update or reinstall the audio driver."),
R("A02","Software",{"no_sound":T,"driver_outdated":F},f_("audio_output_or_hardware"),.5,3,1,"Further Test","Free","Check mute/output device; test with headphones."),
R("A03","Peripherals",{"kb_mouse_fail":T,"usb_dead_all":T},f_("usb_controller_or_driver"),.8,6,2,"Update","Free","Reinstall USB controller drivers; check BIOS USB settings."),
R("A04","Software",{"device_malfunction":T,"driver_outdated":F,"driver_recent_install":T},f_("driver_conflict_new_device"),.7,6,2,"Update","Free","Roll back the recent driver or install the correct version."),
R("A05","Software",{"app_crash_specific":T,"mem_usage_high":T},f_("app_memory_issue"),.65,4,2,"Repair","Free","Close other programs; repair or reinstall the app; add RAM if needed."),
R("A06","Software",{"registry_errors":T,"app_crash_specific":T},f_("registry_issue"),.7,4,2,"Repair","Free","Restore from a restore point; reinstall the affected app."),
]

# ---- Bluetooth & connection-problem knowledge
NET_FIELDS = [
("Network","airplane_mode","Airplane mode is on",None),
("Network","bt_no_toggle","Bluetooth option missing in settings",None),
("Network","bt_not_detected","Bluetooth device (e.g. headphones) not found when scanning",None),
("Network","bt_pairs_no_connect","Bluetooth device pairs but won't connect / keeps disconnecting",None),
("Network","bt_no_sound","Bluetooth headphones connected but no sound",None),
("Network","bt_audio_stutter","Bluetooth audio stutters or lags",None),
("Network","bt_device_low_battery","Headphones/device battery low or not charging",None),
("Network","bt_works_other","Does the headphone/device work with another phone or PC",["yes","no"]),
("Network","wifi_connected_no_internet","Connected to Wi-Fi but 'no internet access'",None),
("Network","wifi_not_listed","Wi-Fi network not shown in the list",None),
("Network","wifi_password_fail","Wi-Fi password rejected / cannot join",None),
("Network","ethernet_no_link","Ethernet cable plugged in but no connection",None),
]
NET_RULES = [
R("B01","Network",{"bt_no_toggle":T},f_("bt_driver_missing"),.8,6,2,"Update","Free","Install/update the Bluetooth driver; start the Bluetooth Support Service; check BIOS."),
R("B02","Network",{"airplane_mode":T,"bt_not_detected":T},f_("airplane_mode_enabled"),.9,9,1,"Repair","Free","Turn off airplane mode, then turn Bluetooth on."),
R("B03","Network",{"bt_not_detected":T,"bt_works_other":"no"},f_("bt_device_faulty_or_discharged"),.8,7,2,"Further Test","Low","Charge and reset the headphones; replace them if no device can find them."),
R("B04","Network",{"bt_not_detected":T,"bt_device_low_battery":T},f_("bt_device_battery_low"),.85,8,1,"Repair","Free","Fully charge the headphones, then put them in pairing mode."),
R("B05","Network",{"bt_not_detected":T,"bt_works_other":"yes","bt_no_toggle":F,"airplane_mode":F},f_("bt_pairing_or_range_issue"),.6,5,1,"Repair","Free","Put the device in pairing mode, move closer, remove the old pairing and pair again."),
R("B06","Network",{"bt_pairs_no_connect":T,"bt_works_other":"yes"},f_("bt_stale_pairing"),.7,6,1,"Repair","Free","Remove (forget) the device, restart Bluetooth, and pair again."),
R("B07","Network",{"bt_pairs_no_connect":T,"driver_outdated":T},f_("bt_driver_issue"),.8,6,2,"Update","Free","Update or reinstall the Bluetooth driver."),
R("B08","Network",{"bt_pairs_no_connect":T,"wifi_drops":T},f_("radio_interference"),.6,4,1,"Further Test","Free","Wi-Fi and Bluetooth share 2.4 GHz: switch the router to 5 GHz and move away from interference."),
R("B09","Network",{"bt_no_sound":T,"bt_pairs_no_connect":F},f_("bt_wrong_output_device"),.75,6,1,"Repair","Free","Select the headphones as the default output device in Sound settings; check volume and mute."),
R("B10","Network",{"bt_no_sound":T,"driver_outdated":T},f_("audio_driver_issue"),.8,5,1,"Update","Free","Update the audio and Bluetooth drivers."),
R("B11","Network",{"bt_audio_stutter":T,"bt_works_other":"yes"},f_("bt_interference_or_range"),.65,5,1,"Repair","Free","Move closer, remove obstacles, avoid 2.4 GHz interference, update the driver."),
R("B12","Network",{"bt_audio_stutter":T,"high_cpu_idle":T},f_("background_process_load"),.6,5,2,"Scan","Free","Close heavy background processes; scan for malware."),
R("B13","Network",{"bt_not_detected":T,"bt_no_toggle":F,"driver_recent_install":T},f_("bt_driver_conflict"),.7,6,2,"Update","Free","Roll back or reinstall the recently changed Bluetooth driver."),
R("B14","Network",{"bt_no_toggle":T,"update_recent":T},f_("bt_driver_missing"),.75,6,2,"Update","Free","Reinstall the Bluetooth driver after the update."),
R("N07","Network",{"wifi_connected_no_internet":T,"other_devices_ok":T,"dns_fail":F},f_("ip_configuration_problem"),.65,5,2,"Repair","Free","Run ipconfig /release and /renew; reset the network stack."),
R("N08","Network",{"wifi_connected_no_internet":T,"other_devices_ok":F},f_("router_or_isp_fault"),.85,6,2,"Repair","Free","Restart router/modem; contact your ISP if it persists."),
R("N09","Network",{"wifi_connected_no_internet":T,"dns_fail":T},f_("dns_issue"),.9,6,1,"Repair","Free","Flush DNS and switch to 8.8.8.8 / 1.1.1.1."),
R("N10","Network",{"wifi_not_listed":T,"airplane_mode":T},f_("airplane_mode_enabled"),.9,9,1,"Repair","Free","Turn off airplane mode and enable Wi-Fi."),
R("N11","Network",{"wifi_not_listed":T,"wifi_adapter_missing":T},f_("faulty_nic"),.8,7,3,"Replace","Low","Replace the network card or use a USB adapter."),
R("N12","Network",{"wifi_not_listed":T,"other_devices_ok":T,"airplane_mode":F,"wifi_adapter_missing":F},f_("wifi_adapter_disabled_or_driver"),.7,5,2,"Update","Free","Enable the Wi-Fi adapter in Device Manager; update the driver."),
R("N13","Network",{"wifi_password_fail":T},f_("wrong_password_or_security_setting"),.7,5,1,"Repair","Free","Forget the network, re-enter the password, check the security type (WPA2/WPA3)."),
R("N14","Network",{"ethernet_no_link":T},f_("ethernet_cable_or_port_fault"),.8,6,2,"Replace","Low","Try another cable and port; check link lights on the router."),
]

# ---- Keyboard / mouse / touchpad knowledge
KB_FIELDS = [
("Software & Peripherals","kb_wireless","Keyboard/mouse is wireless (Bluetooth or USB dongle)",None),
("Software & Peripherals","kb_keys_dead","Some keys are not responding or stuck",None),
("Software & Peripherals","mouse_erratic","Mouse cursor jumps, lags or double-clicks",None),
("Software & Peripherals","touchpad_dead","Laptop touchpad not working",None),
("Software & Peripherals","kb_works_bios","Keyboard works in BIOS but not in Windows",None),
]
KB_RULES = [
R("K01","Peripherals",{"kb_mouse_fail":T,"kb_wireless":T},f_("wireless_peripheral_battery_or_receiver"),.7,5,1,"Further Test","Free","Replace the batteries, re-plug the USB receiver, and re-pair the device."),
R("K02","Peripherals",{"kb_mouse_fail":T,"kb_wireless":T,"bt_pairs_no_connect":T},f_("bt_stale_pairing"),.8,6,1,"Repair","Free","Remove the Bluetooth keyboard/mouse and pair it again."),
R("K03","Peripherals",{"kb_keys_dead":T},f_("keyboard_key_failure"),.75,4,1,"Clean","Low","Clean under the keys; replace the keyboard if keys still fail."),
R("K04","Peripherals",{"mouse_erratic":T},f_("mouse_sensor_or_surface_issue"),.7,4,1,"Clean","Free","Clean the sensor, change the surface, replace batteries, update the driver."),
R("K05","Peripherals",{"touchpad_dead":T},f_("touchpad_disabled_or_driver"),.75,4,1,"Update","Free","Enable the touchpad (Fn key/Settings) and update its driver."),
R("K06","Peripherals",{"kb_mouse_fail":T,"kb_works_bios":T},f_("keyboard_driver_issue"),.85,6,2,"Update","Free","Reinstall the keyboard/HID drivers in Device Manager."),
]

RULES += EXTRA_RULES + NET_RULES + KB_RULES
FIELDS += EXTRA_FIELDS + NET_FIELDS + KB_FIELDS

# Normal baseline states (used only as soft assumptions when unasked, never treated as confirmed facts)
TRUE_DEFAULT = {"fans_spin", "post_ok", "bios_sees_drive", "fan_spinning", "other_devices_ok"}
NORMAL_STATE = {k: (o[0] if o else k in TRUE_DEFAULT) for _, k, _, o in FIELDS}

_keys = {f[1] for f in FIELDS}
assert len({r.id for r in RULES}) == len(RULES) >= 100
for _r in RULES:
    for _k in _r.conds:
        assert _k.startswith(("d:", "fault:")) or _k in _keys, (_r.id, _k)