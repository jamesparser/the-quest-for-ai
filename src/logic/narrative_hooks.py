# src/logic/narrative_hooks.py
import subprocess

class NarrativeHookSystem:
    def __init__(self):
        self.hooks = {}

    def register_hook(self, event_name: str, callback_func):
        if event_name not in self.hooks:
            self.hooks[event_name] = []
        self.hooks[event_name].append(callback_func)

    def trigger_event(self, event_name: str, context: dict):
        if event_name in self.hooks:
            for callback in self.hooks[event_name]:
                callback(context)

def on_archetype_shift(context):
    old_state = context.get('old_state')
    new_state = context.get('new_state')
    print(f"[HOOK FIRED] Archetype transition detected: {old_state} -> {new_state}")
    print("Executing adaptive biocentric alignment check against MeTTa AtomSpace...")
    
    # Optional: Trigger your MeTTa test script or connector here
    try:
        result = subprocess.run(["python3", "test_metta.py"], capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print("[MEKTA SYNC] MeTTa logic validation passed successfully for new archetype state.")
        else:
            print("[MEKTA SYNC] Notice: MeTTa check returned non-zero code.")
    except Exception as e:
        print(f"[MEKTA SYNC] Could not execute MeTTa check directly: {e}")
