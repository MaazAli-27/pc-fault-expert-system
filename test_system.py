from engine import run, decide
from knowledge import RULES, SAMPLES, NORMAL_STATE
from dialogue import parse

EXPECT = {
    "1. Won't power on": "psu_failure",
    "2. Random shutdowns + hot CPU": "cpu_fan_failure",
    "3. Clicking HDD + SMART warning": "hdd_mechanical_failure",
    "4. Beeps + BSODs": "faulty_ram",
    "5. Pop-ups + unknown programs": "malware_infection",
    "6. One device offline": "faulty_nic",
    "7. Boot loop after update": "failed_os_update",
    "8. Artifacts in games, hot GPU": "gpu_overheating",
    "9. Disk 100% + low space": "disk_full_issue",
    "10. Multiple faults": "malware_infection",
    "11. Bluetooth headphones won't connect": "bt_stale_pairing",
    "12. Wi-Fi connected but no internet": "dns_issue",
}

assert set(SAMPLES) == set(EXPECT), f"Mismatch between SAMPLES and EXPECT: {set(SAMPLES) ^ set(EXPECT)}"

for name, s in SAMPLES.items():
    exp = EXPECT[name]
    wm, tr = run(RULES, s, normal_state=NORMAL_STATE)
    faults = decide(wm, tr)
    ids = [f["id"] for f in faults]
    assert "fault:" + exp in ids, (name, ids)
    print(f"PASS {name}: top={faults[0]['name']} ({len(faults)} faults, {len(tr)} rules fired)")
print("Rules in KB:", len(RULES))

# --- tests for the extended rules
EXTRA = [({"swollen_battery":True},"swollen_battery_hazard"),({"laptop_not_charging":True,"battery_drains":True},"battery_worn"),
 ({"freezes":True,"smart_status":"failing"},"storage_failure_freezing"),({"overclocked":True,"bsod":True},"unstable_overclock"),
 ({"screen_cracked":True},"broken_screen"),({"wifi_drops":True},"wifi_adapter_or_driver"),({"login_fail":True},"corrupt_user_profile"),
 ({"update_stuck":True},"update_service_corrupt"),({"email_spam":True},"account_compromised"),({"no_sound":True,"driver_outdated":True},"audio_driver_issue"),
 ({"smart_status":"failing","bad_sectors":True},"drive_end_of_life"),({"external_drive_fail":True},"external_drive_fault")]
for s, exp in EXTRA:
    wm, tr = run(RULES, s, normal_state=NORMAL_STATE)
    assert "fault:" + exp in [f["id"] for f in decide(wm, tr)], (s, exp)
print("PASS extended rules:", len(EXTRA), "| total rules:", len(RULES))

NEW = [({"bt_not_detected":True,"bt_works_other":"no"},"bt_device_faulty_or_discharged"),
 ({"bt_pairs_no_connect":True,"bt_works_other":"yes"},"bt_stale_pairing"),({"bt_no_sound":True},"bt_wrong_output_device"),
 ({"airplane_mode":True,"bt_not_detected":True},"airplane_mode_enabled"),({"bt_no_toggle":True},"bt_driver_missing"),
 ({"wifi_connected_no_internet":True,"dns_fail":True},"dns_issue"),({"wifi_not_listed":True,"wifi_adapter_missing":True},"faulty_nic"),
 ({"wifi_password_fail":True},"wrong_password_or_security_setting"),({"ethernet_no_link":True},"ethernet_cable_or_port_fault")]
for s, exp in NEW:
    wm, tr = run(RULES, s, normal_state=NORMAL_STATE)
    assert "fault:" + exp in [f["id"] for f in decide(wm, tr)], (s, exp)
print("PASS bluetooth/connection rules:", len(NEW), "| total rules:", len(RULES))

KB = [({"kb_mouse_fail":True,"kb_wireless":True},"wireless_peripheral_battery_or_receiver"),({"kb_keys_dead":True},"keyboard_key_failure"),
 ({"mouse_erratic":True},"mouse_sensor_or_surface_issue"),({"touchpad_dead":True},"touchpad_disabled_or_driver"),
 ({"kb_mouse_fail":True,"kb_works_bios":True},"keyboard_driver_issue")]
for s, exp in KB:
    wm, tr = run(RULES, s, normal_state=NORMAL_STATE)
    assert "fault:" + exp in [f["id"] for f in decide(wm, tr)], (s, exp)
print("PASS keyboard/mouse rules:", len(KB), "| total rules:", len(RULES))

# --- test negation & open-world "Don't know" behavior
facts, _ = parse("There is no burning smell and the fan is not loud, but it freezes")
assert facts.get("psu_smell") is False and facts.get("fan_noisy") is False and facts.get("freezes") is True, facts
wm_dk, tr_dk = run(RULES, {"no_internet": True, "other_devices_ok": None}, normal_state=NORMAL_STATE)
assert "fault:faulty_nic" not in wm_dk and "fault:router_or_isp_fault" not in wm_dk
print("PASS negation parsing & open-world 'Don't know' handling")

# --- headless UI test: one full consultation through the Streamlit app
# --- "why this action" rationale and the 'Don't know' interview fix
from knowledge import NORMAL_STATE
from dialogue import next_question
from engine import report
for name, s in SAMPLES.items():
    wm, tr = run(RULES, s, normal_state=NORMAL_STATE)
    fs = decide(wm, tr)
    assert all(f["why_action"] and (f["atype"] in f["why_action"] or "Immediate action" in f["why_action"]) for f in fs), name
    assert "Why this action:" in report(fs, tr), name
nq = next_question({"no_internet": None}, ["no_internet"], [])
assert nq is None or "Network" not in nq[1], nq       # a "Don't know" must not select an area
print("PASS action rationale (cards + report) and Don't-know area fix")

try:
    from streamlit.testing.v1 import AppTest
except ImportError:
    print("SKIP app flow test (streamlit not installed)"); raise SystemExit
at = AppTest.from_file("app.py", default_timeout=60).run(); assert not at.exception, at.exception
at.text_area[0].set_value("computer crashes"); at.run()
[b for b in at.button if "Start consultation" in b.label][0].click().run()
for _ in range(15):
    if at.session_state["stage"] != "interview": break
    if at.radio: at.radio[0].set_value("Yes")
    else: at.selectbox[0].set_value(at.selectbox[0].options[0])
    at.run(); [b for b in at.button if b.label.startswith("Next")][0].click().run(); assert not at.exception, at.exception
assert at.session_state["stage"] == "done"
print("PASS app flow: consultation completed")