from src.logic.narrative_hooks import NarrativeHookSystem, on_archetype_shift

def run_test():
    print("--- Initializing Narrative Hook Test ---")
    hook_sys = NarrativeHookSystem()
    
    # Register our hook
    hook_sys.register_hook("archetype_changed", on_archetype_shift)
    
    # Simulate an event trigger
    hook_sys.trigger_event("archetype_changed", {
        "old_state": "Explorer",
        "new_state": "Scientist",
        "valence": 0.9
    })
    print("--- Test Completed Successfully ---")

if __name__ == "__main__":
    run_test()
