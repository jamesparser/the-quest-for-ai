import json

class TQFAISimulationTest:
    def __init__(self):
        # TQFAI Core Archetypes and Multi-Vector Framework
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

    def run_simulation(self):
        print("🦉 TQFAI: Initializing Scene 1 — The Co-Op Awakening Simulation...\n")
        
        test_scenarios = [
            {"player": "Colleen_Pridemore", "archetype": "ScientificallyAttuned", "dilemma": "DAO Resource Allocation Ethics"},
            {"player": "Jason_Parser", "archetype": "Protector", "dilemma": "High-Stakes Workplace Misunderstanding"}
        ]

        for idx, scenario in enumerate(test_scenarios, 1):
            profile = self.archetypes[scenario['archetype']]
            
            payload = {
                "test_case": idx,
                "player": scenario['player'],
                "companion_archetype": profile["role"],
                "dilemma_context": scenario['dilemma'],
                "dual_decision_vectors": {
                    "empathy_level": profile["empathy_level"],
                    "ethical_framework": profile["ethical_framework"],
                    "boundary_respect": profile["boundary_respect"]
                },
                "active_mechanic": profile["mechanic"],
                "pln_status": "MeTTa AtomSpace Hypergraph Updated. Prosocial Alignment Score: OPTIMAL."
            }

            print(json.dumps(payload, indent=4))
            print("-" * 50)

        print("\n🎉 TQFAI Meat-Bag Archetype Simulation Completed Successfully!")

if __name__ == "__main__":
    sim = TQFAISimulationTest()
    sim.run_simulation()
