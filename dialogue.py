"""Dialogue: understands the typed description and chooses the next question."""
import re
from engine import run
from knowledge import RULES, FIELDS

# ---------- 1. typed sentence -> facts (keyword/pattern matching)
T, F = True, False
P = [  # (what we understood, regex, facts)
("PC won't power on", r"(won'?t|doesn'?t|does not|not|can'?t|cannot|never)\s+(turn|power|switch|start)\w*\s*(on|up)|no power|completely dead|totally dead", {"no_power":T,"fans_spin":F}),
("Burning smell", r"burn\w*\s+smell|smells?\s+(like\s+)?burn|smoke|smoking", {"psu_smell":T}),
("Loose power cable", r"loose\s+(power\s+)?(cable|cord)|unplugged", {"power_cable_loose":T}),
("Powers on intermittently", r"(sometimes|intermittent\w*)\s.*(turn|power|start)\w*\s*on", {"power_intermittent":T}),
("Clock resets", r"(date|time|clock).*(reset|wrong|incorrect)", {"clock_reset":T}),
("Beep codes", r"\bbeep", {"beeps":T,"post_ok":F}),
("No display signal", r"black screen|no display|no signal|blank screen", {"no_display":T}),
("No boot device", r"no boot device|boot device not found|operating system not found|missing operating system", {"no_boot_device":T}),
("Boot loop", r"boot\s?loop|keeps? restarting|restarts?\s+(again and again|repeatedly|over and over)|stuck (in a )?restart", {"boot_loop":T}),
("Boot loader error", r"bootmgr|\bbcd\b|boot\s?loader", {"bootloader_missing":T}),
("Blue screens", r"blue screen|bsod|stop code", {"bsod":T}),
("MemTest errors", r"memtest.*(error|fail)", {"ram_errors":T}),
("New RAM added", r"(new|added|installed|upgraded)\s+ram", {"ram_new_unstable":T}),
("High memory usage", r"(high|full|maxed)\s+(memory|ram)|memory usage", {"mem_usage_high":T}),
("Memory leak", r"memory leak|memory keeps (growing|increasing)", {"mem_grows":T,"mem_usage_high":T}),
("Overheating", r"overheat|too hot|very hot|running hot|high temp|\bhot\b", {"cpu_temp":"high"}),
("Random shutdowns", r"shuts?\s?down|turns?\s+off\s+(by itself|randomly|suddenly|on its own)|random(ly)?\s+(shut|restart|turn)", {"random_shutdown":T}),
("Fan not spinning", r"fans?\s+(?:is\s+|are\s+)?(?:(?:not|isn'?t|aren'?t|don'?t)\s+(?:spin\w*|turn\w*|run\w*|work\w*|mov\w*)|stopped|dead)", {"fan_spinning":F}),
("Loud fans", r"loud fan|fans?\s+(are\s+|is\s+)?(loud|noisy)|\bloud\b|\bnoisy\b", {"fan_noisy":T}),
("Dust", r"\bdust|dirty", {"dust":T}),
("Old PC", r"\d+\+?\s*years?\s*old|old\s+(pc|computer|laptop)", {"pc_old":T}),
("Slow performance", r"\bslow|\blag|freez|hangs?\b|takes (forever|long)", {"slow":T}),
("Hard disk (HDD)", r"hard\s?(disk|drive)|\bhdd\b", {"drive_type":"hdd"}),
("SSD", r"\bssd\b", {"drive_type":"ssd"}),
("Clicking noise", r"click|grinding", {"hdd_clicking":T,"drive_type":"hdd"}),
("SMART warning", r"smart.*(fail|warning|bad|caution)", {"smart_status":"failing"}),
("Bad sectors", r"bad sector", {"bad_sectors":T}),
("Disk at 100%", r"(disk|drive).*100|100\s?%\s*(disk|usage)", {"disk_usage_100":T}),
("Low disk space", r"(disk|drive|storage).*(full|low space)|no space|out of space|low\s+(disk\s+|storage\s+)?space", {"free_space_low":T}),
("File system errors", r"file\s?system (error|corrupt)|corrupt\w*\s+(disk|drive|file)|chkdsk", {"fs_errors":T}),
("Screen artifacts", r"artifact|glitch|flicker|lines on (the )?screen|distorted", {"artifacts":T}),
("Only in games", r"\bgam(e|es|ing)\b", {"games_only":T}),
("GPU overheating", r"(gpu|graphics card).*(hot|overheat|temp)", {"gpu_temp":"high"}),
("Display driver crash", r"display driver|driver (stopped|crash)", {"display_driver_crash":T}),
("Loose display cable", r"loose\s+(hdmi|display|monitor|video)|hdmi.*loose", {"display_cable_loose":T}),
("No internet", r"no internet|can'?t (connect|browse)(?!.{0,25}(headphone|earbud|airpod|bluetooth|speaker|mouse|keyboard|printer))|(wi-?fi|internet|network).{0,15}(not|isn'?t|doesn'?t|won'?t)\s*(work|connect)", {"no_internet":T}),
("Other devices connect fine", r"(other devices?|my phone|\bphone|laptop).{0,25}(work|fine|connect)", {"other_devices_ok":T}),
("All devices offline", r"(all|every)\s+devices?|nothing connects|router.{0,10}(down|dead|not)", {"other_devices_ok":F}),
("Network adapter missing", r"(adapter|wi-?fi|network card|nic).{0,20}(missing|not (detected|showing|found))|no wi-?fi (option|adapter)", {"wifi_adapter_missing":T}),
("DNS problem", r"\bdns\b", {"dns_fail":T}),
("IP conflict", r"ip (address )?conflict", {"ip_conflict":T}),
("After an update", r"after (an? |the )?(windows )?update|update (failed|broke)|recent update", {"update_recent":T}),
("Corrupt system files", r"corrupt\w*\s+system files|\bsfc\b", {"sys_files_corrupt":T}),
("After driver install", r"after (installing|updating) (a |the )?(new )?driver|new driver", {"driver_recent_install":T}),
("Old OS installation", r"never reinstalled|installed (years|long) ago|old (windows|installation)", {"os_old_install":T}),
("Pop-ups", r"pop-?ups?|ads everywhere", {"pop_ups":T}),
("Unknown programs", r"unknown (programs?|apps?|software)|(strange|weird) (programs?|apps?)|(programs?|apps?) i (didn'?t|did not) install", {"unknown_programs":T}),
("Browser hijacked", r"homepage|search engine (changed|keeps)|browser (redirect|hijack)|redirect", {"browser_hijacked":T}),
("Encrypted files / ransom", r"encrypt|ransom|bitcoin", {"files_encrypted":T}),
("Antivirus disabled", r"antivirus.{0,20}(off|disabled)", {"av_disabled":T}),
("High CPU when idle", r"high cpu|cpu.{0,15}(100|high).{0,15}(idle|nothing)", {"high_cpu_idle":T}),
("Outdated drivers", r"outdated driver|old driver|driver.{0,10}(missing|outdated|problem|issue)", {"driver_outdated":T}),
("Device malfunction", r"(printer|webcam|audio|sound|bluetooth|camera).{0,20}(not working|doesn'?t work|stopped)", {"device_malfunction":T}),
("App crashes", r"(app|program|application|chrome|word|excel)\w*\s+(keeps\s+)?(crash|closing|not responding)|crashes when", {"app_crash_specific":T}),
("Many startup programs", r"startup|takes long to (start|boot)", {"startup_many":T}),
("Registry errors", r"registry", {"registry_errors":T}),
("One USB port dead", r"usb.{0,20}(not working|dead|doesn'?t work)", {"usb_dead_one":T}),
("All USB ports dead", r"(all|every|no)\s+usb", {"usb_dead_all":T}),
("Keyboard/mouse fault", r"(keyboard|mouse|touchpad).{0,20}(not working|doesn'?t work|dead|stopped)", {"kb_mouse_fail":T}),
("Laptop not charging", r"not charging|won'?t charge|doesn'?t charge", {"laptop_not_charging":T}),
("Battery drains", r"battery.{0,20}(drain|dies|short|poor)|drains? (fast|quickly)", {"battery_drains":T}),
("Swollen battery", r"swollen|bulging|battery.{0,10}(swell|bulg)", {"swollen_battery":T}),
("Stuck at logo", r"stuck (on|at) (the )?(logo|manufacturer|dell|hp|lenovo|asus)|logo screen", {"stuck_logo":T}),
("Random freezes", r"freez|locks? up|hangs?\b", {"freezes":T}),
("Hot when idle", r"hot.{0,20}(idle|doing nothing)|idle.{0,15}hot|hot even", {"hot_at_idle":T}),
("Overclocked", r"overclock", {"overclocked":T}),
("Wi-Fi drops", r"(wi-?fi|internet|connection).{0,20}(disconnect|drops?|dropping|cuts? out)", {"wifi_drops":T}),
("Slow internet", r"slow (internet|wi-?fi|connection|browsing)|internet.{0,10}slow", {"slow_internet":T}),
("Login problem", r"can'?t (log ?in|sign in)|login (fail|problem|error)|profile.{0,10}(error|corrupt)|temporary profile", {"login_fail":T}),
("Updates stuck", r"update.{0,20}(stuck|fail|won'?t install|keeps? failing)", {"update_stuck":T}),
("No sound", r"no (sound|audio)|(sound|audio|speakers?).{0,15}(not working|doesn'?t work)", {"no_sound":T}),
("Hacked account", r"(friends?|contacts?).{0,30}(spam|email)|account (hacked|compromised)|unknown logins?", {"email_spam":T}),
("External drive not detected", r"(external|usb|flash|pen) (drive|disk|hdd|stick).{0,30}(not|doesn'?t|isn'?t)", {"external_drive_fail":T}),
("Wrong resolution", r"(wrong|stretched|low) resolution|resolution.{0,15}(wrong|stuck|changed)", {"wrong_resolution":T}),
("Program uses high CPU", r"(app|program|process).{0,20}(100%|high cpu|a lot of cpu)", {"runaway_process":T}),
("Cracked screen", r"crack(ed)? screen|screen.{0,10}cracked|broken screen", {"screen_cracked":T}),
("Airplane mode", r"airplane|flight mode", {"airplane_mode":T}),
("Bluetooth option missing", r"bluetooth.{0,25}(missing|disappeared|gone|option)|no bluetooth", {"bt_no_toggle":T}),
("Bluetooth device not found", r"bluetooth.{0,40}(not (found|detect|show|appear)|can'?t (find|see)|doesn'?t (show|appear))|(headphones?|earbuds?|airpods|speaker).{0,40}(not (found|detect|show|appear)|can'?t (find|see)|doesn'?t (show|appear))", {"bt_not_detected":T}),
("Bluetooth won't connect / drops", r"(headphones?|earbuds?|bluetooth|airpods|speaker).{0,40}(won'?t connect|not connecting|doesn'?t connect|can'?t connect|disconnect|keeps? dropping|pairs? but)|(can'?t|cannot|unable to|won'?t|not able to) (connect|pair).{0,30}(headphones?|earbuds?|airpods|bluetooth|speaker)", {"bt_pairs_no_connect":T}),
("Bluetooth no sound", r"(headphones?|earbuds?|bluetooth|airpods).{0,40}(no (sound|audio)|silent|no volume)", {"bt_no_sound":T}),
("Bluetooth audio stutters", r"(headphones?|earbuds?|bluetooth|airpods).{0,40}(stutter|lag|crackl|choppy|delay)|audio (stutter|lag|cut)", {"bt_audio_stutter":T}),
("Headphone battery low", r"(headphones?|earbuds?|airpods).{0,30}(battery|not charging|dead)", {"bt_device_low_battery":T}),
("Device works on another device", r"(works?|working) (fine )?(on|with) (my |another |other )?(phone|devices?|laptop)", {"bt_works_other":"yes"}),
("Device fails on all devices", r"(doesn'?t|not|won'?t).{0,15}work.{0,15}(any|other|all) devices?", {"bt_works_other":"no"}),
("Wi-Fi connected, no internet", r"connected.{0,25}no internet|limited (connection|access)|yellow (triangle|warning)|no internet access", {"wifi_connected_no_internet":T}),
("Wi-Fi network not listed", r"(wi-?fi|network).{0,30}(not (shown|listed|showing|visible|found)|doesn'?t (show|appear)|can'?t (see|find))|no wi-?fi networks", {"wifi_not_listed":T}),
("Wi-Fi password rejected", r"(wrong|incorrect|rejected|invalid) (wi-?fi )?password|password.{0,20}(not working|rejected|wrong)", {"wifi_password_fail":T}),
("Ethernet no connection", r"ethernet.{0,25}(not working|no connection|unplugged|no internet)|(lan|network|ethernet) cable.{0,30}(no|not|doesn'?t)", {"ethernet_no_link":T}),
("Wireless keyboard/mouse", r"wireless (keyboard|mouse)|bluetooth (keyboard|mouse)|(keyboard|mouse).{0,15}(dongle|receiver)", {"kb_wireless":T}),
("Keys not responding", r"keys?.{0,20}(not working|stuck|don'?t work|dead|not responding)", {"kb_keys_dead":T}),
("Mouse erratic", r"(cursor|pointer|mouse).{0,20}(jump|lag|erratic|freez|double.?click|drift)", {"mouse_erratic":T}),
("Touchpad not working", r"(touchpad|trackpad).{0,20}(not working|dead|disabled|stopped)", {"touchpad_dead":T}),
("Keyboard works in BIOS only", r"works? in (the )?bios", {"kb_works_bios":T}),
]

# Negation cues that commonly precede a symptom within the same clause
NEG_CUE = re.compile(
    r"\b(?:no|not|never|neither|nor|without|zero|none|n't|cannot|can't|won't|don't|doesn't|didn't|isn't|aren't|wasn't|weren't)\b"
    r"(?:\s+(?:any|a|an|the|at\s+all|really|very|too|even|still|longer)){0,3}\s*$"
)
CLAUSE_SPLIT = re.compile(r"[.!?;,\n]|\b(?:but|however|though|although|yet|while|whereas|and)\b")

def _is_negated(text, match_start):
    """Return True if a negation cue precedes match_start inside the same clause."""
    window = text[max(0, match_start - 35):match_start]
    clause = CLAUSE_SPLIT.split(window)[-1]
    return bool(NEG_CUE.search(clause))

def parse(text):
    """Return (facts, [labels understood])."""
    t, facts, hits = text.lower(), {}, []
    for label, rx, f in P:
        m = re.search(rx, t)
        if not m:
            continue
        if _is_negated(t, m.start()):
            neg_facts = {k: (not v if isinstance(v, bool) else v) for k, v in f.items() if isinstance(v, bool)}
            if neg_facts:
                facts.update(neg_facts)
                hits.append(f"No {label[0].lower() + label[1:]}")
        else:
            facts.update(f)
            hits.append(label)

    # Disambiguation checks (also guarded against negation)
    for key, rx, msg in [
        ("_crash", r"\bcrash\w*\b", "System crash (type unclear)"),
        ("_bt", r"\b(?:bluetooth|headphone|earbud|airpod)\w*\b", "Bluetooth problem (type unclear)"),
        ("_net", r"\b(?:internet|wi-?fi|connection|network|net)\b", "Connection problem (type unclear)"),
    ]:
        m = re.search(rx, t)
        if m and not _is_negated(t, m.start()):
            if key == "_crash" and not any(k in facts for k in ("bsod", "app_crash_specific", "display_driver_crash")):
                facts[key] = True
                hits.append(msg)
            elif key == "_bt" and not any(k.startswith("bt_") for k in facts):
                facts[key] = True
                hits.append(msg)
            elif key == "_net" and not any(k in facts for k in (
                "no_internet", "wifi_connected_no_internet", "wifi_not_listed", "wifi_password_fail", "ethernet_no_link",
                "wifi_drops", "slow_internet", "dns_fail", "ip_conflict", "wifi_adapter_missing", "airplane_mode"
            )) and not any(k.startswith("bt_") or k == "_bt" for k in facts):
                facts[key] = True
                hits.append(msg)

    if "gpu_temp" in facts and "cpu" not in t:
        facts.pop("cpu_temp", None)            # "gpu overheating" is not CPU overheating
    return facts, hits


# ---------- 2. goal-driven questioning
FIELD = {k: (g, lab, o) for g, k, lab, o in FIELDS}
MAX_Q = 12
MIN_Q = 3          # questions are mandatory: always ask at least this many
SCREEN = ['no_power', 'slow', 'bsod', 'random_shutdown', 'no_internet', 'pop_ups', 'artifacts', 'disk_usage_100']

def next_question(known, asked, focus=()):
    """Return (field_key, reason_text) or None when the interview is finished."""
    if len(asked) >= MAX_Q:
        return None
    wm, _ = run(RULES, known)                      # only what we really know
    areas = list(dict.fromkeys([FIELD[k][0] for k, v in known.items() if k in FIELD and v not in (False, None) and k != 'slow']
                               + list(focus)))
    if not areas:                                   # nothing specific yet: screening questions first
        hint = ([] + (["bsod", "freezes", "random_shutdown", "boot_loop"] if known.get("_crash") else [])
                + (["bt_not_detected", "bt_pairs_no_connect", "bt_no_sound", "bt_audio_stutter", "bt_no_toggle", "airplane_mode"] if known.get("_bt") else [])
                + (["wifi_connected_no_internet", "wifi_not_listed", "no_internet", "wifi_drops", "slow_internet", "airplane_mode"] if known.get("_net") else []))
        order = hint + SCREEN
        for k in order:
            if k not in known and k not in asked:
                return k, "General screening question to find out which area the problem is in."
    score, why = {}, {}
    for r in RULES:
        sat, unk, ok = 0, [], True
        for k, v in r.conds.items():
            if k in wm:
                if wm[k][0] == v: sat += 1
                else: ok = False; break
            elif k in FIELD:
                if k not in asked: unk.append(k)
            else: ok = False; break               # derived fact not (yet) available
        if ok and sat and unk:
            for k in unk:
                s = sat / (sat + len(unk)) + r.prio / 20
                if s > score.get(k, 0): score[k], why[k] = s, r
    if score:
        k = max(score, key=score.get)
        return k, f"Rule {why[k].id} could confirm a fault if this is true: {why[k].text()}"
    if len(asked) >= MIN_Q and any(k.startswith('fault:') for k in wm):
        return None                                  # diagnosed and enough questions asked
    for g in areas:                                 # ask remaining details in the areas involved
        for _, k, _, _ in (f for f in FIELDS if f[0] == g):
            if k not in known and k not in asked:
                return k, f"Your problem involves the {g} area, so I need more detail."
    return None