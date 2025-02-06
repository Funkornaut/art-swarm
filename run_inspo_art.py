from art_agents import InspoAgent, ArtistAgent
from PIL import Image
import io

def run_art_generation():
    # Create instances of both agents
    inspo_agent = InspoAgent()
    artist_agent = ArtistAgent()
    
    # Get inspiration from InspoAgent
    print("\n=== Getting Onchain Inspiration ===")
    inspiration = inspo_agent.get_onchain_inspiration()
    print("Generated inspiration:", inspiration)
    
    # Generate art script using ArtistAgent
    print("\n=== Generating Art Script ===")
    script = artist_agent.generate_art_script(inspiration)
    print("\nGenerated script:")
    print(script)
    
    # Execute the script to create art
    print("\n=== Executing Art Script ===")
    collection = artist_agent.execute_script(script)
    print(f"\nGenerated {len(collection)} pieces")
    
    # Save the generated art
    if collection:
        img = Image.open(io.BytesIO(collection[0]))
        img.save('generated_art.png')
        print("\nSaved first piece as 'generated_art.png'")
        img = Image.open(io.BytesIO(collection[1]))
        img.save('generated_art_2.png')
        print("\nSaved second piece as 'generated_art_2.png'")
        img = Image.open(io.BytesIO(collection[2]))
        img.save('generated_art_3.png')
        print("\nSaved third piece as 'generated_art_3.png'")

if __name__ == "__main__":
    run_art_generation()