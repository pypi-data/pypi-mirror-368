"""
Pokemon name normalization and fuzzing utilities.

This module handles the normalization of Pokemon names to match the expected
data format, including handling special cases, forms, and variations.
"""

from typing import Optional


class PokemonNameNormalizer:
    """
    Handles normalization of Pokemon names for data lookup.
    
    This class contains logic to handle various Pokemon name variations,
    special forms, and edge cases to ensure proper data retrieval.
    """
    
    @staticmethod
    def normalize_name(name: str) -> str:
        """
        Normalize a Pokemon name for data lookup.
        
        Args:
            name: The input Pokemon name
            
        Returns:
            Normalized name that should match the data format
        """
        # Handle spaces and hyphens
        if ' ' in name:
            name = name.strip()
            name = name.replace("   ","-")
            name = name.replace("  ", "-")
            name = name.replace(' ', '-')
            name = name.replace('---', '-')
            name = name.replace('--', '-')
            name = name.replace('- -', '-')
            name = name.replace(' - ', '-')
            name = name.replace(' -', '-')
            name = name.replace('- ', '-')

        

        # Handle special cases
        name = PokemonNameNormalizer._handle_special_cases(name)
        
        # Convert to lowercase at the end
        return name.lower()
    
    @staticmethod
    def _handle_special_cases(name: str) -> str:
        """
        Handle special Pokemon name cases and forms.
        
        Args:
            name: The name to process
            
        Returns:
            Processed name
        """
        name_lower = name.lower()
        
        # Aegislash forms
        if 'aegislash' in name_lower:
            if 'blade' in name_lower:
                return 'aegislash-blade'
            elif 'shield' in name_lower:
                return 'aegislash-shield'
            else:
                return 'aegislash-blade'
        
        if 'alcremie' in name_lower:
            if 'gmax' in name_lower:
                return 'alcremie-gmax'
            else:
                return 'alcremie'
        
        # Arceus forms
        if 'arceus' in name_lower:
            return 'arceus'
        
        # Basculin forms
        if 'basculin' in name_lower:
            if 'blue' in name_lower:
                return 'basculin-blue-striped'
            elif 'red' in name_lower:
                return 'basculin-red-striped'
            elif 'white' in name_lower:
                return 'basculin-white-striped'
            else:
                return 'basculin-blue-striped'
        
        if 'basculegion' in name_lower:
            if 'f' in name_lower:
                return 'basculegion-female'
            elif 'm' in name_lower:
                return 'basculegion-male'
            else:
                return 'basculegion-female'
        
        # Calyrex forms
        if 'calyrex' in name_lower:
            if 'ice' in name_lower:
                return 'calyrex-ice'
            elif 'shadow' in name_lower:
                return 'calyrex-shadow'
            else:
                return 'calyrex-ice'
        
        # Castform forms
        if 'castform' in name_lower:
            if 'rainy' in name_lower:
                return 'castform-rainy'
            elif 'snowy' in name_lower:
                return 'castform-snowy'
            elif 'sunny' in name_lower:
                return 'castform-sunny'
            else:
                return 'castform-sunny'
        
        if 'cramorant' in name_lower:
            if 'gulping' in name_lower:
                return 'cramorant-gulping'
            elif 'gorging' in name_lower:
                return 'cramorant-gorging'
            else:
                return 'cramorant'
        
        # Darmanitan forms
        if 'darmanitan' in name_lower:
            if 'zen' in name_lower:
                return 'darmanitan-zen'
            else:
                return 'darmanitan-standard'
        
        # Deoxys forms
        if 'deoxys' in name_lower:
            if 'attack' in name_lower:
                return 'deoxys-attack'
            elif 'defense' in name_lower:
                return 'deoxys-defense'
            elif 'speed' in name_lower:
                return 'deoxys-speed'
            elif 'normal' in name_lower:
                return 'deoxys-normal'
            else:
                return 'deoxys'
        
        # Dialga forms
        if 'dialga' in name_lower:
            if 'origin' in name_lower:
                return 'dialga-origin'
            else:
                return 'dialga'
        
        # Dudunsparce forms
        if 'dudunsparce' in name_lower:
            if 'three' in name_lower:
                return 'dudunsparce-three-segment'
            else:
                return 'dudunsparce-two-segment'
        
        # Eevee forms
        if 'eevee' in name_lower:
            if 'starter' in name_lower:
                return 'eevee-starter'
            else:
                return 'eevee'
        
        # Eiscue forms
        if 'eiscue' in name_lower:
            if 'noice' in name_lower:
                return 'eiscue-noice'
            else:
                return 'eiscue-ice'
        
        # Enamorus forms
        if 'enamorus' in name_lower:
            if 'therian' in name_lower:
                return 'enamorus-therian'
            else:
                return 'enamorus-incarnate'
        
        # Floette forms
        if 'floette' in name_lower:
            if 'eternal' in name_lower:
                return 'floette-eternal'
            else:
                return 'floette'
        
        # Florges forms
        if 'florges' in name_lower:
            return 'florges'
        
        if 'gastrodon' in name_lower:
            return 'gastrodon'
        
        # Gimmighoul forms
        if 'gimmighoul' in name_lower:
            if 'roaming' in name_lower:
                return 'gimmighoul-roaming'
            else:
                return 'gimmighoul'
        
        # Giratina forms
        if 'giratina' in name_lower:
            if 'origin' in name_lower:
                return 'giratina-origin'
            else:
                return 'giratina-altered'
        
        # Gourgeist forms
        if 'gourgeist' in name_lower:
            if 'large' in name_lower:
                return 'gourgeist-large'
            elif 'small' in name_lower:
                return 'gourgeist-small'
            elif 'super' in name_lower:
                return 'gourgeist-super'
            else:
                return 'gourgeist-average'
        
        # Greninja forms
        if 'greninja' in name_lower:
            if 'ash' in name_lower:
                return 'greninja-ash'
            elif 'battle' in name_lower:
                return 'greninja-battle-bond'
            else:
                return 'greninja'
        
        # Hoopa forms
        if 'hoopa' in name_lower:
            if 'unbound' in name_lower:
                return 'hoopa-unbound'
            else:
                return 'hoopa'
        
        # Indeedee forms
        if 'indeedee' in name_lower:
            if 'f' in name_lower:
                return 'indeedee-female'
            elif 'm' in name_lower:
                return 'indeedee-male'
            else:
                return 'indeedee-female'
        
        # Keldeo forms
        if 'keldeo' in name_lower:
            if 'resolute' in name_lower:
                return 'keldeo-resolute'
            else:
                return 'keldeo-ordinary'
        
        # Koraidon forms
        if 'koraidon' in name_lower:
            if 'gliding' in name_lower:
                return 'koraidon-gliding-build'
            elif 'limited' in name_lower:
                return 'koraidon-limited-build'
            elif 'sprinting' in name_lower:
                return 'koraidon-sprinting-build'
            elif 'swimming' in name_lower:
                return 'koraidon-swimming-build'
            else:
                return 'koraidon'
        
        # Kyurem forms
        if 'kyurem' in name_lower:
            if 'black' in name_lower:
                return 'kyurem-black'
            elif 'white' in name_lower:
                return 'kyurem-white'
            else:
                return 'kyurem'
        
        # Landorus forms
        if 'landorus' in name_lower:
            if 'therian' in name_lower:
                return 'landorus-therian'
            else:
                return 'landorus-incarnate'
        
        # Lycanroc forms
        if 'lycanroc' in name_lower:
            if 'dusk' in name_lower:
                return 'lycanroc-dusk'
            elif 'midday' in name_lower:
                return 'lycanroc-midday'
            else:
                return 'lycanroc-midnight'
        
        # Magearna forms
        if 'magearna' in name_lower:
            if 'original' in name_lower:
                return 'magearna-original'
            else:
                return 'magearna'
        
        # Maushold forms
        if 'maushold' in name_lower:
            return 'maushold'
        
        if 'meowstic' in name_lower:
            if 'f' in name_lower:
                return 'meowstic-female'
            else:
                return 'meowstic-male'
        
        if 'meloetta' in name_lower:
            if 'aria' in name_lower:
                return 'meloetta-aria'
            elif 'pirouette' in name_lower:
                return 'meloetta-pirouette'
            else:
                return 'meloetta-aria'
        
        # Mimikyu forms
        if 'mimikyu' in name_lower:
            if 'busted' in name_lower:
                return 'mimikyu-busted'
            else:
                return 'mimikyu-disguised'
        
        # Minior forms
        if 'minior' in name_lower:
            if 'blue' in name_lower:
                if 'meteor' in name_lower:
                    return 'minior-blue-meteor'
                else:
                    return 'minior-blue'
            elif 'green' in name_lower:
                if 'meteor' in name_lower:
                    return 'minior-green-meteor'
                else:
                    return 'minior-green'
            elif 'indigo' in name_lower:
                if 'meteor' in name_lower:
                    return 'minior-indigo-meteor'
                else:
                    return 'minior-indigo'
            elif 'orange' in name_lower:
                if 'meteor' in name_lower:
                    return 'minior-orange-meteor'
                else:
                    return 'minior-orange'
            elif 'red' in name_lower:
                if 'meteor' in name_lower:
                    return 'minior-red-meteor'
                else:
                    return 'minior-red'
            elif 'violet' in name_lower:
                if 'meteor' in name_lower:
                    return 'minior-violet-meteor'
                else:
                    return 'minior-violet'
            elif 'yellow' in name_lower:
                if 'meteor' in name_lower:
                    return 'minior-yellow-meteor'
                else:
                    return 'minior-yellow'
            else:
                return 'minior-red'
        
        # Miraidon forms
        if 'miraidon' in name_lower:
            if 'aquatic' in name_lower:
                return 'miraidon-aquatic-mode'
            elif 'drive' in name_lower:
                return 'miraidon-drive-mode'
            elif 'glide' in name_lower:
                return 'miraidon-glide-mode'
            elif 'low' in name_lower:
                return 'miraidon-low-power-mode'
            else:
                return 'miraidon'
        
        if 'morpeko' in name_lower:
            if 'full-belly' in name_lower:
                return 'morpeko-full-belly'
            else:
                return 'morpeko-hangry'
        
        if 'necrozma' in name_lower:
            if 'dawn' in name_lower:
                return 'necrozma-dawn'
            elif 'dusk' in name_lower:
                return 'necrozma-dusk'
            elif 'ultra' in name_lower:
                return 'necrozma-ultra'
            else:
                return 'necrozma'
        
        # Nidoran forms
        if 'nidoran' in name_lower:
            if 'f' in name_lower:
                return 'nidoran-f'
            else:
                return 'nidoran-m'
        
        # Ogerpon forms
        if 'ogerpon' in name_lower:
            if 'cornerstone' in name_lower:
                return 'ogerpon-cornerstone-mask'
            elif 'wellspring' in name_lower:
                return 'ogerpon-wellspring-mask'
            elif 'hearthflame' in name_lower:
                return 'ogerpon-hearthflame-mask'
            else:
                return 'ogerpon'
        
        if 'oinkologne' in name_lower:
            if 'f' in name_lower:
                return 'oinkologne-female'
            elif 'm' in name_lower:
                return 'oinkologne-male'
            else:
                return 'oinkologne-female'
        
        #Oricorio forms
        if 'oricorio' in name_lower:
            if 'baile' in name_lower:
                return 'oricorio-baile'
            elif 'pa' in name_lower:
                return 'oricorio-pau'
            elif 'sensu' in name_lower:
                return 'oricorio-sensu'
            elif 'pom' in name_lower:
                return 'oricorio-pom-pom'
            else:
                return 'oricorio-baile'
        
        # Palafin forms
        if 'palafin' in name_lower:
            if 'hero' in name_lower:
                return 'palafin-hero'
            else:
                return 'palafin-zero'
        
        # Palkia forms
        if 'palkia' in name_lower:
            if 'origin' in name_lower:
                return 'palkia-origin'
            else:
                return 'palkia'
        
        # Pikachu forms
        if 'pikachu' in name_lower:
            if 'alola' in name_lower:
                return 'pikachu-alola-cap'
            elif 'belle' in name_lower:
                return 'pikachu-belle'
            elif 'cosplay' in name_lower:
                return 'pikachu-cosplay'
            elif 'hoenn' in name_lower:
                return 'pikachu-hoenn-cap'
            elif 'kalos' in name_lower:
                return 'pikachu-kalos-cap'
            elif 'libre' in name_lower:
                return 'pikachu-libre'
            elif 'original' in name_lower:
                return 'pikachu-original-cap'
            elif 'partner' in name_lower:
                return 'pikachu-partner-cap'
            elif 'phd' in name_lower:
                return 'pikachu-phd'
            elif 'pop' in name_lower:
                return 'pikachu-pop-star'
            elif 'rock' in name_lower:
                return 'pikachu-rock-star'
            elif 'sinnoh' in name_lower:
                return 'pikachu-sinnoh-cap'
            elif 'starter' in name_lower:
                return 'pikachu-starter'
            elif 'unova' in name_lower:
                return 'pikachu-unova-cap'
            elif 'world' in name_lower:
                return 'pikachu-world-cap'
            else:
                return 'pikachu'
        
        if 'polteageist' in name_lower:
            return 'polteageist'
        
        if 'poltchageist' in name_lower:
            return 'poltchageist'
        
        if 'porygon-z' in name_lower:
            return 'porygon-z'
        
        # Pumpkaboo forms
        if 'pumpkaboo' in name_lower:
            if 'large' in name_lower:
                return 'pumpkaboo-large'
            elif 'small' in name_lower:
                return 'pumpkaboo-small'
            elif 'super' in name_lower:
                return 'pumpkaboo-super'
            else:
                return 'pumpkaboo-average'
        
        # Rockruff forms
        if 'rockruff' in name_lower:
            if 'own' in name_lower:
                return 'rockruff-own-tempo'
            else:
                return 'rockruff'
        
        # Rotom forms
        if 'rotom' in name_lower:
            if 'fan' in name_lower:
                return 'rotom-fan'
            elif 'frost' in name_lower:
                return 'rotom-frost'
            elif 'heat' in name_lower:
                return 'rotom-heat'
            elif 'mow' in name_lower:
                return 'rotom-mow'
            elif 'wash' in name_lower:
                return 'rotom-wash'
            else:
                return 'rotom'
        
        if 'sawsbuck' in name_lower:
            return 'sawsbuck'
        
        # Shaymin forms
        if 'shaymin' in name_lower:
            if 'sky' in name_lower:
                return 'shaymin-sky'
            else:
                return 'shaymin-land'
        
        if 'sinistcha' in name_lower:
            return 'sinistcha'
        
        if 'sinistea' in name_lower:
            return 'sinistea'
        
        # Squawkabilly forms
        if 'squawkabilly' in name_lower:
            if 'blue' in name_lower:
                return 'squawkabilly-blue-plumage'
            elif 'red' in name_lower:
                return 'squawkabilly-red-plumage'
            elif 'white' in name_lower:
                return 'squawkabilly-white-plumage'
            elif 'green' in name_lower:
                return 'squawkabilly-green-plumage'
            else:
                return 'squawkabilly-white-plumage'
        
        # Tapu forms
        if 'tapu' in name_lower:
            if 'bulu' in name_lower:
                return 'tapu-bulu'
            elif 'fini' in name_lower:
                return 'tapu-fini'
            elif 'koko' in name_lower:
                return 'tapu-koko'
            elif 'lele' in name_lower:
                return 'tapu-lele'
            else:
                return 'tapu-koko'
        
        # Tauros Paldea forms
        if 'tauros' in name_lower and 'paldea' in name_lower:
            if 'blaze' in name_lower:
                return 'tauros-paldea-blaze-breed'
            elif 'aqua' in name_lower:
                return 'tauros-paldea-aqua-breed'
            elif 'combat' in name_lower:
                return 'tauros-paldea-combat-breed'
            else:
                return 'tauros-paldea-blaze-breed'
        
        # Tatsugiri forms
        if 'tatsugiri' in name_lower:
            if 'curly' in name_lower:
                return 'tatsugiri-curly'
            elif 'droopy' in name_lower:
                return 'tatsugiri-droopy'
            else:
                return 'tatsugiri-stretchy'
        
        # Terapagos forms
        if 'terapagos' in name_lower:
            if 'stellar' in name_lower:
                return 'terapagos-stellar'
            elif 'terastal' in name_lower:
                return 'terapagos-terastal'
            else:
                return 'terapagos'
        
        # Thundurus forms
        if 'thundurus' in name_lower:
            if 'therian' in name_lower:
                return 'thundurus-therian'
            else:
                return 'thundurus-incarnate'
        
        # Tornadus forms
        if 'tornadus' in name_lower:
            if 'therian' in name_lower:
                return 'tornadus-therian'
            else:
                return 'tornadus-incarnate'
        
        # Toxtricity forms
        if 'toxtricity' in name_lower:
            if 'amped' in name_lower:
                return 'toxtricity-amped'
            else:
                return 'toxtricity-low-key'
        
        if 'urshifu' in name_lower:
            if 'single' in name_lower:
                return 'urshifu-single-strike'
            elif 'rapid' in name_lower:
                return 'urshifu-rapid-strike'
            else:
                return 'urshifu-single-strike'
        
        # Ursaluna forms
        if 'ursaluna' in name_lower:
            if 'bloodmoon' in name_lower:
                return 'ursaluna-bloodmoon'
            else:
                return 'ursaluna'
        
        if 'vivillon' in name_lower:
            return 'vivillon'
        
        # Wishiwashi forms
        if 'wishiwashi' in name_lower:
            if 'school' in name_lower:
                return 'wishiwashi-school'
            else:
                return 'wishiwashi-solo'
        
        # Wormadam forms
        if 'wormadam' in name_lower:
            if 'sandy' in name_lower:
                return 'wormadam-sandy'
            elif 'trash' in name_lower:
                return 'wormadam-trash'
            else:
                return 'wormadam-plant'
        
        if 'zacian' in name_lower:
            if 'crowned' in name_lower:
                return 'zacian-crowned'
            else:
                return 'zacian'
        
        if 'zamazenta' in name_lower:
            if 'crowned' in name_lower:
                return 'zamazenta-crowned'
            else:
                return 'zamazenta'
        
        # Zarude forms
        if 'zarude' in name_lower:
            if 'dada' in name_lower:
                return 'zarude-dada'
            else:
                return 'zarude'
        
        # Zygarde forms
        if 'zygarde' in name_lower:
            if 'complete' in name_lower:
                return 'zygarde-complete'
            elif '10' in name_lower:
                if 'power' in name_lower:
                    return 'zygarde-10-power-construct'
                else:
                    return 'zygarde-10'
            elif '50' in name_lower:
                if 'power' in name_lower:
                    return 'zygarde-50-power-construct'
                else:
                    return 'zygarde-50'
            else:
                return 'zygarde-50'
        
        return name 