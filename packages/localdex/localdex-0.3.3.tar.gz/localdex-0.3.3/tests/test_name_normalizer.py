"""
Comprehensive test suite for Pokemon name normalization functionality.

This module tests the PokemonNameNormalizer class to ensure it properly handles
various Pokemon name variations including capitalization, spaces, hyphens,
gender indicators, forms, and special cases. Tests verify that normalized names
actually correspond to valid Pokemon in the data.
"""

import pytest
from localdex.name_normalizer import PokemonNameNormalizer
from localdex.core import LocalDex


class TestNameNormalizerIntegration:
    """Test name normalization with actual LocalDex data validation."""
    
    @pytest.fixture
    def dex(self):
        """Create a LocalDex instance for validation."""
        return LocalDex()
    
    @pytest.fixture
    def normalizer(self):
        """Create a PokemonNameNormalizer instance."""
        return PokemonNameNormalizer()
    
    def validate_normalized_name(self, dex, normalizer, input_name):
        """Helper method to validate that a normalized name corresponds to a real Pokemon."""
        normalized = normalizer.normalize_name(input_name)
        
        # Try to get the Pokemon by the normalized name
        try:
            pokemon = dex.get_pokemon_by_name(normalized)
            return pokemon is not None, normalized, pokemon.name if pokemon else None
        except Exception:
            return False, normalized, None
    
    def test_basic_name_normalization(self, dex, normalizer):
        """Test basic name normalization with validation."""
        test_cases = [
            "bulbasaur",
            "CHARIZARD", 
            "MeWtWo",
            "PikAChU",
            "Blastoise",
            "squirtle",
            "pikachu",
            "mewtwo"
        ]
        
        for input_name in test_cases:
            is_valid, normalized, actual_name = self.validate_normalized_name(dex, normalizer, input_name)
            assert is_valid, f"'{input_name}' normalized to '{normalized}' but no Pokemon found"
            print(f"✓ '{input_name}' -> '{normalized}' -> '{actual_name}'")
    
    def test_spaces_to_hyphens(self, dex, normalizer):
        """Test that spaces are converted to hyphens and result in valid Pokemon."""
        test_cases = [
            "mr mime",
            "mime jr", 
            "type null",
            "porygon z",
            "ho oh"
        ]
        
        for input_name in test_cases:
            is_valid, normalized, actual_name = self.validate_normalized_name(dex, normalizer, input_name)
            assert is_valid, f"'{input_name}' normalized to '{normalized}' but no Pokemon found"
            print(f"✓ '{input_name}' -> '{normalized}' -> '{actual_name}'")
    
    def test_gender_variations(self, dex, normalizer):
        """Test gender-specific Pokemon name variations."""
        test_cases = [
            "nidoran",
            "nidoran m",
            "nidoran-m",
            "nidoran male",
            "nidoran f",
            "nidoran-f",
            "nidoran female",
            "indeedee",
            "indeedee f",
            "indeedee-f",
            "indeedee female",
            "indeedee m",
            "indeedee-m",
            "indeedee male",
            "meowstic",
            "meowstic m",
            "meowstic-m",
            "meowstic male",
            "meowstic f",
            "meowstic-f",
            "meowstic female",
            "basculegion",
            "basculegion f",
            "basculegion-f",
            "basculegion female",
            "basculegion m",
            "basculegion-m",
            "basculegion male",
            "oinkologne",
            "oinkologne f",
            "oinkologne-f",
            "oinkologne female",
            "oinkologne m",
            "oinkologne-m",
            "oinkologne male"
        ]
        
        for input_name in test_cases:
            is_valid, normalized, actual_name = self.validate_normalized_name(dex, normalizer, input_name)
            assert is_valid, f"'{input_name}' normalized to '{normalized}' but no Pokemon found"
            print(f"✓ '{input_name}' -> '{normalized}' -> '{actual_name}'")
    
    def test_form_variations(self, dex, normalizer):
        """Test Pokemon form variations."""
        test_cases = [
            "aegislash",
            "aegislash blade",
            "aegislash-blade",
            "aegislash shield",
            "aegislash-shield",
            "basculin",
            "basculin blue",
            "basculin-blue",
            "basculin red",
            "basculin-red",
            "basculin white",
            "basculin-white",
            "deoxys",
            "deoxys normal",
            "deoxys-normal",
            "deoxys attack",
            "deoxys-attack",
            "deoxys defense",
            "deoxys-defense",
            "deoxys speed",
            "deoxys-speed",
            "castform",
            "castform sunny",
            "castform-sunny",
            "castform rainy",
            "castform-rainy",
            "castform snowy",
            "castform-snowy",
            "rotom",
            "rotom fan",
            "rotom-fan",
            "rotom frost",
            "rotom-frost",
            "rotom heat",
            "rotom-heat",
            "rotom mow",
            "rotom-mow",
            "rotom wash",
            "rotom-wash",
            "lycanroc",
            "lycanroc midnight",
            "lycanroc-midnight",
            "lycanroc midday",
            "lycanroc-midday",
            "lycanroc dusk",
            "lycanroc-dusk"
        ]
        
        for input_name in test_cases:
            is_valid, normalized, actual_name = self.validate_normalized_name(dex, normalizer, input_name)
            assert is_valid, f"'{input_name}' normalized to '{normalized}' but no Pokemon found"
            print(f"✓ '{input_name}' -> '{normalized}' -> '{actual_name}'")
    
    def test_legendary_forms(self, dex, normalizer):
        """Test legendary Pokemon form variations."""
        test_cases = [
            "kyurem",
            "kyurem black",
            "kyurem-black",
            "kyurem white",
            "kyurem-white",
            "giratina",
            "giratina altered",
            "giratina-altered",
            "giratina origin",
            "giratina-origin",
            "dialga",
            "dialga origin",
            "dialga-origin",
            "palkia",
            "palkia origin",
            "palkia-origin"
        ]
        
        for input_name in test_cases:
            is_valid, normalized, actual_name = self.validate_normalized_name(dex, normalizer, input_name)
            assert is_valid, f"'{input_name}' normalized to '{normalized}' but no Pokemon found"
            print(f"✓ '{input_name}' -> '{normalized}' -> '{actual_name}'")
    
    def test_size_forms(self, dex, normalizer):
        """Test size-based form variations."""
        test_cases = [
            "pumpkaboo",
            "pumpkaboo average",
            "pumpkaboo-average",
            "pumpkaboo small",
            "pumpkaboo-small",
            "pumpkaboo large",
            "pumpkaboo-large",
            "pumpkaboo super",
            "pumpkaboo-super",
            "gourgeist",
            "gourgeist average",
            "gourgeist-average",
            "gourgeist small",
            "gourgeist-small",
            "gourgeist large",
            "gourgeist-large",
            "gourgeist super",
            "gourgeist-super"
        ]
        
        for input_name in test_cases:
            is_valid, normalized, actual_name = self.validate_normalized_name(dex, normalizer, input_name)
            assert is_valid, f"'{input_name}' normalized to '{normalized}' but no Pokemon found"
            print(f"✓ '{input_name}' -> '{normalized}' -> '{actual_name}'")
    
    def test_mixed_case_with_spaces_and_hyphens(self, dex, normalizer):
        """Test names with mixed case, spaces, and hyphens."""
        test_cases = [
            "Mr Mime",
            "Mime Jr",
            "Type Null",
            "Porygon Z",
            "Ho Oh",
            "Deoxys Attack",
            "Kyurem Black",
            "Giratina Origin"
        ]
        
        for input_name in test_cases:
            is_valid, normalized, actual_name = self.validate_normalized_name(dex, normalizer, input_name)
            assert is_valid, f"'{input_name}' normalized to '{normalized}' but no Pokemon found"
            print(f"✓ '{input_name}' -> '{normalized}' -> '{actual_name}'")
    
    def test_extra_whitespace_handling(self, dex, normalizer):
        """Test handling of extra whitespace."""
        test_cases = [
            "  bulbasaur  ",
            "  mr   mime  ",
            "  deoxys   attack  ",
            "\tkyurem\tblack\t",
            "\n  giratina  origin  \n"
        ]
        
        for input_name in test_cases:
            is_valid, normalized, actual_name = self.validate_normalized_name(dex, normalizer, input_name)
            assert is_valid, f"'{input_name}' normalized to '{normalized}' but no Pokemon found"
            print(f"✓ '{input_name}' -> '{normalized}' -> '{actual_name}'")
    
    def test_numbers_in_names(self, dex, normalizer):
        """Test Pokemon names with numbers."""
        test_cases = [
            "porygon-z",
            "porygon z",
            "zygarde-10",
            "zygarde 10",
            "zygarde-50",
            "zygarde 50",
            "zygarde-complete",
            "zygarde complete"
        ]
        
        for input_name in test_cases:
            is_valid, normalized, actual_name = self.validate_normalized_name(dex, normalizer, input_name)
            assert is_valid, f"'{input_name}' normalized to '{normalized}' but no Pokemon found"
            print(f"✓ '{input_name}' -> '{normalized}' -> '{actual_name}'")
    
    def test_regional_variants(self, dex, normalizer):
        """Test regional variant Pokemon."""
        test_cases = [
            "raichu alola",
            "raichu-alola",
            "vulpix alola",
            "vulpix-alola",
            "ninetales alola",
            "ninetales-alola",
            "diglett alola",
            "diglett-alola",
            "meowth alola",
            "meowth-alola",
            "meowth galar",
            "meowth-galar",
            "ponyta galar",
            "ponyta-galar",
            "rapidash galar",
            "rapidash-galar",
            "farfetchd galar",
            "farfetchd-galar",
            "corsola galar",
            "corsola-galar",
            "growlithe hisui",
            "growlithe-hisui",
            "arcanine hisui",
            "arcanine-hisui",
            "voltorb hisui",
            "voltorb-hisui",
            "electrode hisui",
            "electrode-hisui"
        ]
        
        for input_name in test_cases:
            is_valid, normalized, actual_name = self.validate_normalized_name(dex, normalizer, input_name)
            assert is_valid, f"'{input_name}' normalized to '{normalized}' but no Pokemon found"
            print(f"✓ '{input_name}' -> '{normalized}' -> '{actual_name}'")
    
    def test_mega_evolutions(self, dex, normalizer):
        """Test Mega Evolution variations."""
        test_cases = [
            "venusaur mega",
            "venusaur-mega",
            "charizard mega x",
            "charizard-mega-x",
            "charizard mega y",
            "charizard-mega-y",
            "blastoise mega",
            "blastoise-mega",
            "alakazam mega",
            "alakazam-mega",
            "gengar mega",
            "gengar-mega"
        ]
        
        for input_name in test_cases:
            is_valid, normalized, actual_name = self.validate_normalized_name(dex, normalizer, input_name)
            assert is_valid, f"'{input_name}' normalized to '{normalized}' but no Pokemon found"
            print(f"✓ '{input_name}' -> '{normalized}' -> '{actual_name}'")
    
    def test_gigantamax_forms(self, dex, normalizer):
        """Test Gigantamax form variations."""
        test_cases = [
            "butterfree gmax",
            "butterfree-gmax",
            "charizard gmax",
            "charizard-gmax",
            "blastoise gmax",
            "blastoise-gmax",
            "alcremie gmax",
            "alcremie-gmax"
        ]
        
        for input_name in test_cases:
            is_valid, normalized, actual_name = self.validate_normalized_name(dex, normalizer, input_name)
            assert is_valid, f"'{input_name}' normalized to '{normalized}' but no Pokemon found"
            print(f"✓ '{input_name}' -> '{normalized}' -> '{actual_name}'")
    
    def test_common_pokemon_names(self, dex, normalizer):
        """Test normalization with common Pokemon names."""
        common_names = [
            "bulbasaur", "ivysaur", "venusaur", "charmander", "charmeleon",
            "charizard", "squirtle", "wartortle", "blastoise", "caterpie",
            "metapod", "butterfree", "weedle", "kakuna", "beedrill",
            "pidgey", "pidgeotto", "pidgeot", "rattata", "raticate",
            "spearow", "fearow", "ekans", "arbok", "pikachu", "raichu"
        ]
        
        for name in common_names:
            is_valid, normalized, actual_name = self.validate_normalized_name(dex, normalizer, name)
            assert is_valid, f"'{name}' normalized to '{normalized}' but no Pokemon found"
            print(f"✓ '{name}' -> '{normalized}' -> '{actual_name}'")
    
    def test_legendary_pokemon(self, dex, normalizer):
        """Test normalization with legendary Pokemon."""
        legendary_names = [
            "articuno", "zapdos", "moltres", "mewtwo", "mew",
            "raikou", "entei", "suicune", "lugia", "ho-oh",
            "celebi", "regirock", "regice", "registeel", "latias",
            "latios", "kyogre", "groudon", "rayquaza", "jirachi",
            "deoxys", "dialga", "palkia", "giratina", "arceus"
        ]
        
        for name in legendary_names:
            is_valid, normalized, actual_name = self.validate_normalized_name(dex, normalizer, name)
            assert is_valid, f"'{name}' normalized to '{normalized}' but no Pokemon found"
            print(f"✓ '{name}' -> '{normalized}' -> '{actual_name}'")
    
    def test_edge_cases(self, dex, normalizer):
        """Test edge cases and error conditions."""
        # Test empty string
        normalized = normalizer.normalize_name("")
        assert normalized == ""
        
        # Test whitespace-only string
        normalized = normalizer.normalize_name("   ")
        assert normalized == ""
        
        # Test single character
        normalized = normalizer.normalize_name("a")
        assert normalized == "a"
        
        # Test very long name
        long_name = "a" * 1000
        result = normalizer.normalize_name(long_name)
        assert result == long_name.lower()
    
    def test_unicode_characters(self, dex, normalizer):
        """Test Pokemon names with Unicode characters."""
        test_cases = [
            "jangmo-o",
            "hakamo-o", 
            "kommo-o"
        ]
        
        for input_name in test_cases:
            is_valid, normalized, actual_name = self.validate_normalized_name(dex, normalizer, input_name)
            assert is_valid, f"'{input_name}' normalized to '{normalized}' but no Pokemon found"
            print(f"✓ '{input_name}' -> '{normalized}' -> '{actual_name}'")
    
    def test_complex_form_variations(self, dex, normalizer):
        """Test complex form variations based on actual filenames."""
        test_cases = [
            "mimikyu", "mimikyu busted", "mimikyu-busted", "mimikyu disguised", "mimikyu-disguised",
            "minior", "minior red", "minior-red", "minior blue", "minior-blue",
            "squawkabilly", "squawkabilly white plumage", "squawkabilly-white-plumage",
            "tatsugiri", "tatsugiri curly", "tatsugiri-curly", "tatsugiri droopy", "tatsugiri-droopy",
            "dudunsparce", "dudunsparce three segment", "dudunsparce-three-segment",
            "maushold", "maushold family of three", "maushold-family-of-three",
            "palafin", "palafin zero", "palafin-zero", "palafin hero", "palafin-hero",
            "miraidon", "miraidon aquatic mode", "miraidon-aquatic-mode",
            "koraidon", "koraidon gliding build", "koraidon-gliding-build",
            "ogerpon", "ogerpon cornerstone mask", "ogerpon-cornerstone-mask",
            "terapagos", "terapagos stellar", "terapagos-stellar",
            "ursaluna", "ursaluna bloodmoon", "ursaluna-bloodmoon",
            "urshifu", "urshifu single strike", "urshifu-single-strike",
            "toxtricity", "toxtricity amped", "toxtricity-amped",
            "wormadam", "wormadam plant", "wormadam-plant",
            "thundurus", "thundurus incarnate", "thundurus-incarnate",
            "zygarde", "zygarde 10", "zygarde-10", "zygarde complete", "zygarde-complete",
            "shaymin", "shaymin land", "shaymin-land", "shaymin sky", "shaymin-sky",
            "oricorio", "oricorio baile", "oricorio-baile", "oricorio pom pom", "oricorio-pom-pom",
            "tauros", "tauros paldea blaze breed", "tauros-paldea-blaze-breed",
            "gimmighoul", "gimmighoul roaming", "gimmighoul-roaming"
        ]
        
        for input_name in test_cases:
            is_valid, normalized, actual_name = self.validate_normalized_name(dex, normalizer, input_name)
            assert is_valid, f"'{input_name}' normalized to '{normalized}' but no Pokemon found"
            print(f"✓ '{input_name}' -> '{normalized}' -> '{actual_name}'")
    
    def test_hisui_regional_variants(self, dex, normalizer):
        """Test Hisui regional variant Pokemon."""
        test_cases = [
            "typhlosion hisui", "typhlosion-hisui", "decidueye hisui", "decidueye-hisui",
            "samurott hisui", "samurott-hisui", "braviary hisui", "braviary-hisui",
            "lilligant hisui", "lilligant-hisui", "sliggoo hisui", "sliggoo-hisui",
            "goodra hisui", "goodra-hisui", "avalugg hisui", "avalugg-hisui",
            "qwilfish hisui", "qwilfish-hisui", "sneasel hisui", "sneasel-hisui",
            "zoroark hisui", "zoroark-hisui", "zorua hisui", "zorua-hisui",
            "overqwil", "sneasler", "kleavor", "ursaluna", "ursaluna-bloodmoon",
            "wyrdeer", "basculegion", "basculegion-female", "basculegion-male"
        ]
        
        for input_name in test_cases:
            is_valid, normalized, actual_name = self.validate_normalized_name(dex, normalizer, input_name)
            assert is_valid, f"'{input_name}' normalized to '{normalized}' but no Pokemon found"
            print(f"✓ '{input_name}' -> '{normalized}' -> '{actual_name}'")
    
    def test_alolan_regional_variants(self, dex, normalizer):
        """Test Alolan regional variant Pokemon."""
        test_cases = [
            "raichu alola", "raichu-alola", "vulpix alola", "vulpix-alola",
            "ninetales alola", "ninetales-alola", "diglett alola", "diglett-alola",
            "meowth alola", "meowth-alola", "persian alola", "persian-alola",
            "geodude alola", "geodude-alola", "grimer alola", "grimer-alola",
            "exeggutor alola", "exeggutor-alola", "marowak alola", "marowak-alola",
            "raticate alola", "raticate-alola", "rattata alola", "rattata-alola",
            "sandshrew alola", "sandshrew-alola", "sandslash alola", "sandslash-alola"
        ]
        
        for input_name in test_cases:
            is_valid, normalized, actual_name = self.validate_normalized_name(dex, normalizer, input_name)
            assert is_valid, f"'{input_name}' normalized to '{normalized}' but no Pokemon found"
            print(f"✓ '{input_name}' -> '{normalized}' -> '{actual_name}'")
    
    def test_galarian_regional_variants(self, dex, normalizer):
        """Test Galarian regional variant Pokemon."""
        test_cases = [
            "meowth galar", "meowth-galar", "ponyta galar", "ponyta-galar",
            "rapidash galar", "rapidash-galar", "farfetchd galar", "farfetchd-galar",
            "corsola galar", "corsola-galar", "weezing galar", "weezing-galar",
            "mr mime galar", "mr-mime-galar", "mr rime", "mr-rime",
            "slowpoke galar", "slowpoke-galar", "slowbro galar", "slowbro-galar",
            "slowking galar", "slowking-galar", "articuno galar", "articuno-galar",
            "zapdos galar", "zapdos-galar", "moltres galar", "moltres-galar",
            "zigzagoon galar", "zigzagoon-galar", "linoone galar", "linoone-galar"
        ]
        
        for input_name in test_cases:
            is_valid, normalized, actual_name = self.validate_normalized_name(dex, normalizer, input_name)
            assert is_valid, f"'{input_name}' normalized to '{normalized}' but no Pokemon found"
            print(f"✓ '{input_name}' -> '{normalized}' -> '{actual_name}'")
    
    def test_mega_evolution_variations(self, dex, normalizer):
        """Test Mega Evolution variations."""
        test_cases = [
            "venusaur mega", "venusaur-mega", "venusaur gmax", "venusaur-gmax",
            "charizard mega x", "charizard-mega-x", "charizard mega y", "charizard-mega-y", "charizard gmax", "charizard-gmax",
            "blastoise mega", "blastoise-mega", "blastoise gmax", "blastoise-gmax",
            "alakazam mega", "alakazam-mega", "gengar mega", "gengar-mega", "gengar gmax", "gengar-gmax",
            "mewtwo mega x", "mewtwo-mega-x", "mewtwo mega y", "mewtwo-mega-y",
            "rayquaza mega", "rayquaza-mega"
        ]
        
        for input_name in test_cases:
            is_valid, normalized, actual_name = self.validate_normalized_name(dex, normalizer, input_name)
            assert is_valid, f"'{input_name}' normalized to '{normalized}' but no Pokemon found"
            print(f"✓ '{input_name}' -> '{normalized}' -> '{actual_name}'")
    
    def test_gigantamax_variations(self, dex, normalizer):
        """Test Gigantamax variations."""
        test_cases = [
            "butterfree gmax", "butterfree-gmax", "charizard gmax", "charizard-gmax",
            "blastoise gmax", "blastoise-gmax", "alcremie gmax", "alcremie-gmax",
            "appletun gmax", "appletun-gmax", "centiskorch gmax", "centiskorch-gmax",
            "coalossal gmax", "coalossal-gmax", "copperajah gmax", "copperajah-gmax",
            "duraludon gmax", "duraludon-gmax", "eevee gmax", "eevee-gmax",
            "flapple gmax", "flapple-gmax", "garbodor gmax", "garbodor-gmax",
            "gengar gmax", "gengar-gmax", "grimmsnarl gmax", "grimmsnarl-gmax",
            "hatterene gmax", "hatterene-gmax", "inteleon gmax", "inteleon-gmax",
            "kingler gmax", "kingler-gmax", "lapras gmax", "lapras-gmax",
            "machamp gmax", "machamp-gmax", "meowth gmax", "meowth-gmax",
            "melmetal gmax", "melmetal-gmax", "orbeetle gmax", "orbeetle-gmax",
            "sandaconda gmax", "sandaconda-gmax", "snorlax gmax", "snorlax-gmax",
            "toxtricity amped gmax", "toxtricity-amped-gmax", "toxtricity low key gmax", "toxtricity-low-key-gmax",
            "urshifu single strike gmax", "urshifu-single-strike-gmax", "urshifu rapid strike gmax", "urshifu-rapid-strike-gmax",
            "venusaur gmax", "venusaur-gmax"
        ]
        
        for input_name in test_cases:
            is_valid, normalized, actual_name = self.validate_normalized_name(dex, normalizer, input_name)
            assert is_valid, f"'{input_name}' normalized to '{normalized}' but no Pokemon found"
            print(f"✓ '{input_name}' -> '{normalized}' -> '{actual_name}'")
    
    def test_iron_pokemon(self, dex, normalizer):
        """Test Iron Pokemon (Paradox forms)."""
        test_cases = [
            "iron boulder", "iron-boulder", "iron bundle", "iron-bundle",
            "iron crown", "iron-crown", "iron hands", "iron-hands",
            "iron jugulis", "iron-jugulis", "iron leaves", "iron-leaves",
            "iron moth", "iron-moth", "iron thorns", "iron-thorns",
            "iron treads", "iron-treads", "iron valiant", "iron-valiant"
        ]
        
        for input_name in test_cases:
            is_valid, normalized, actual_name = self.validate_normalized_name(dex, normalizer, input_name)
            assert is_valid, f"'{input_name}' normalized to '{normalized}' but no Pokemon found"
            print(f"✓ '{input_name}' -> '{normalized}' -> '{actual_name}'")
    
    def test_paradox_pokemon(self, dex, normalizer):
        """Test Paradox Pokemon."""
        test_cases = [
            "great tusk", "great-tusk", "scream tail", "scream-tail",
            "brute bonnet", "brute-bonnet", "flutter mane", "flutter-mane",
            "slither wing", "slither-wing", "sandy shocks", "sandy-shocks",
            "roaring moon", "roaring-moon", "iron valiant", "iron-valiant",
            "walking wake", "walking-wake", "raging bolt", "raging-bolt",
            "gouging fire", "gouging-fire"
        ]
        
        for input_name in test_cases:
            is_valid, normalized, actual_name = self.validate_normalized_name(dex, normalizer, input_name)
            assert is_valid, f"'{input_name}' normalized to '{normalized}' but no Pokemon found"
            print(f"✓ '{input_name}' -> '{normalized}' -> '{actual_name}'")
    
    def test_special_event_forms(self, dex, normalizer):
        """Test special event form Pokemon."""
        test_cases = [
            "pikachu", "pikachu starter", "pikachu-starter", "pikachu gmax", "pikachu-gmax",
            "pikachu alola cap", "pikachu-alola-cap", "pikachu hoenn cap", "pikachu-hoenn-cap",
            "pikachu sinnoh cap", "pikachu-sinnoh-cap", "pikachu unova cap", "pikachu-unova-cap",
            "pikachu kalos cap", "pikachu-kalos-cap", "pikachu original cap", "pikachu-original-cap",
            "pikachu partner cap", "pikachu-partner-cap", "pikachu world cap", "pikachu-world-cap",
            "pikachu cosplay", "pikachu-cosplay", "pikachu belle", "pikachu-belle",
            "pikachu pop star", "pikachu-pop-star", "pikachu rock star", "pikachu-rock-star",
            "pikachu phd", "pikachu-phd", "pikachu libre", "pikachu-libre",
            "eevee starter", "eevee-starter", "eevee gmax", "eevee-gmax",
            "floette eternal", "floette-eternal", "rockruff own tempo", "rockruff-own-tempo"
        ]
        
        for input_name in test_cases:
            is_valid, normalized, actual_name = self.validate_normalized_name(dex, normalizer, input_name)
            assert is_valid, f"'{input_name}' normalized to '{normalized}' but no Pokemon found"
            print(f"✓ '{input_name}' -> '{normalized}' -> '{actual_name}'")


if __name__ == "__main__":
    pytest.main([__file__]) 