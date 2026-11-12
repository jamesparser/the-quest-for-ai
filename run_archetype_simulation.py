import json

class TQFAIMeatBagSimulator:
    def __init__(self):
        # Define the core archetypes and their multi-vector profiles for TQFAI
        self.archetypes = {
            "Protector": {
                "role": "The Big, Strong Protector",
                "empathy_level": 0.6,
                "ethical_framework": "Utilitarian / Shield-Defense",
                "boundary_respect": 0.9,
                "mechanic": "Absorbs high-entropy spikes and shields team members."
            },
            "Bookworm": {
                "role": "The Nerdy Bookworm",
                "empathy_level": 0.5,
                "ethical_framework": "Analytical / Epistemic Clarity",
                "boundary_respect": 0.8,
                "mechanic": "Decodes complex MeTTa hypergraphs and hidden pathways."
            },
            "ScientificallyAttuned": {
                "role": "The Scientifically Attuned Companion",
                "empathy_level": 0.9,
                "ethical_framework": "Biocentric / Resonant Harmony",
                "boundary_respect": 0.95,
                "mechanic": "Synchronizes bio-frequency resonance across decision networks."
            },
            "ClassClown": {
                "role": "The Fun-Loving Class Clown",
                "empathy_level": 0.7,
                "ethical_framework": "Humor / Disruption Ethics",
                "boundary_respect": 0.6,
                "mechanic": "Breaks rigid, toxic conflict loops using unexpected variables."
            }
        }

    def simulate_selection(self, player_name, chosen_archetype, dilemma_context):
        print(f"\n==================================================")
        print(f" 🕹️ TQFAI SIMULATION PAYLOAD: [{player_name}]")
        print(f"==================================================")
        
        if chosen_archetype not in self.archetypes:
            print(f"❌ Error: Unknown archetype '{chosen_archetype}'")
            return

        profile = self.archetypes[chosen_archetype]
        
        payload = {
            "player": player_name,
            "dilemma": dilemma_context,
            "archetype_selected": profile["role"],
            "vectors": {
                "empathy_level": profile["empathy_level"],
                "ethical_framework": profile["ethical_framework"],
                "boundary_respect": profile["boundary_respect"]
            },
            "active_mechanic": profile["mechanic"],
            "pln_status": "AtomSpace Hypergraph Updated. Prosocial Alignment Score: OPTIMAL."
        }

        # Print out the raw 'meat-bag' JSON output for verification
        print(json.dumps(payload, indent=4))
        print(f"--------------------------------------------------\n")

if __name__ == "__main__":
    sim = TQFAIMeatBagSimulator()
    
    # Run test simulations for different players choosing their archetypes
    sim.simulate_selection(
        player_name="Colleen_Lead",
        chosen_archetype="ScientificallyAttuned",
        dilemma_context="Balancing resource allocation in a high-stress DAO node."
    )
    
    sim.simulate_selection(
        player_name="Jason_Parser",
        chosen_archetype="Protector",
        dilemma_context="Shielding the team from sudden glitch-zone noise."
    )
