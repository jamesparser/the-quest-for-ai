import os

class TQFAIMettaEngine:
    def __init__(self, logic_dir="src/logic"):
        self.logic_dir = logic_dir
        self.archetypes_file = os.path.join(logic_dir, "scene1_archetypes.metta")
        self.biocentric_file = os.path.join(logic_dir, "biocentric_rules.metta")
        
        self.atom_space = {}
        self.load_logic_files()

    def load_logic_files(self):
        """Loads and parses MeTTa logic files into memory for simulation."""
        print("🧠 TQFAI Engine: Initializing AtomSpace from MeTTa layers...")
        
        # Load Archetypes
        if os.path.exists(self.archetypes_file):
            with open(self.archetypes_file, 'r', encoding='utf-8') as f:
                self.archeven_content = f.read()
            print(f"  ✅ Loaded: {self.archetypes_file}")
        else:
            print(f"  ❌ Warning: Missing {self.archetypes_file}")

        # Load Biocentric Rules
        if os.path.exists(self.biocentric_file):
            with open(self.biocentric_file, 'r', encoding='utf-8') as f:
                self.bio_content = f.read()
            print(f"  ✅ Loaded: {self.biocentric_file}")
        else:
            print(f"  ❌ Warning: Missing {self.biocentric_file}")

    def process_player_choice(self, player_id, chosen_archetype, environment_state="Normal"):
        """
        Simulates parsing a player's choice against the MeTTa AtomSpace rules.
        Handles archetype selection and entropy-to-shade transitions.
        """
        print(f"\n🎮 Processing Choice for Player: {player_id}")
        print(f"   Selected Archetype: {chosen_archetype}")
        print(f"   Current Environment State: {environment_state}")

        # Simulated AtomSpace evaluation based on biocentric rules
        if chosen_archetype == "ScientificallyAttuned":
            resonance = "432Hz-HeartCode Active"
            action = "Synchronizing bio-frequency harmony."
        elif chosen_archetype == "Protector":
            resonance = "Shield-Vector Active"
            action = "Absorbing high-entropy spikes."
        elif chosen_archetype == "Bookworm":
            resonance = "Epistemic Clarity Active"
            action = "Decoding MeTTa hypergraph pathways."
        elif chosen_archetype == "ClassClown":
            resonance = "Entropy-Disruption Active"
            action = "Neutralizing toxic conflict loops with humor."
        else:
            resonance = "Standard Baseline"
            action = "Initializing co-op session."

        if environment_state == "HighEntropyLoop":
            effect = "Triggering Shade Protocol & Backpropagation via Mycelial Network."
        else:
            effect = "Maintaining homeostatic balance."

        result = {
            "player": player_id,
            "archetype": chosen_archetype,
            "resonance": resonance,
            "action": action,
            "system_effect": effect
        }
        
        return result

# --- Quick Test Execution ---
if __name__ == "__main__":
    engine = TQFAIMettaEngine()
    
    # Simulate a player picking the Scientifically Attuned companion during a high-entropy event
    outcome = engine.process_player_choice(
        player_id="Agent_L",
        chosen_archetype="ScientificallyAttuned",
        environment_state="HighEntropyLoop"
    )
    
    print("\n--- AtomSpace Evaluation Result ---")
    for k, v in outcome.items():
        print(f"  * {k.capitalize()}: {v}")
