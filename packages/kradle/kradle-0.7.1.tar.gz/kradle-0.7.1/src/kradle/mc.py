"""
Minecraft game element types derived from the minecraft-data npm package.

This module provides programmatic access to Minecraft game elements including blocks,
items, entities, and biomes. All type data is sourced from the minecraft-data npm
package (https://github.com/PrismarineJS/minecraft-data) which is the official
data source for Mineflayer and related tools.

Example usage:
    from kradle import MC

    # Reference blocks by their enum value
    MC.blocks.DIAMOND_ORE      # A diamond ore block
    MC.blocks.CRAFTING_TABLE   # A crafting table block

    # Reference items by their enum value
    MC.items.DIAMOND_PICKAXE   # A diamond pickaxe item
    MC.items.GOLDEN_APPLE      # A golden apple item

    # Reference entities by their enum value
    MC.entities.ZOMBIE         # A zombie entity
    MC.entities.VILLAGER       # A villager entity

    # Reference biomes by their enum value
    MC.biomes.PLAINS          # Plains biome
    MC.biomes.DESERT          # Desert biome
"""

from enum import Enum
from typing import Any, Final


class MCEnum(str, Enum):
    """Base class for Minecraft enums that automatically returns values."""

    def __str__(self) -> str:
        return str(self.value)

    def __repr__(self) -> str:
        return str(self.value)

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, str):
            return str(self.value) == other
        return super().__eq__(other)

    def __new__(cls, value: Any) -> "MCEnum":
        obj = str.__new__(cls, value)
        obj._value_ = value
        return obj


class MCBlocks(MCEnum):
    """Block types representing all placeable blocks in Minecraft.

    All values are sourced from minecraft-data and match the game's internal identifiers.
    """

    ACACIA_BUTTON = "acacia_button"
    """Acacia Button (ID: 389)"""

    ACACIA_DOOR = "acacia_door"
    """Acacia Door (ID: 586)"""

    ACACIA_FENCE = "acacia_fence"
    """Acacia Fence (ID: 578)"""

    ACACIA_FENCE_GATE = "acacia_fence_gate"
    """Acacia Fence Gate (ID: 570)"""

    ACACIA_HANGING_SIGN = "acacia_hanging_sign"
    """Acacia Hanging Sign (ID: 211)"""

    ACACIA_LEAVES = "acacia_leaves"
    """Acacia Leaves (ID: 86)"""

    ACACIA_LOG = "acacia_log"
    """Acacia Log (ID: 50)"""

    ACACIA_PLANKS = "acacia_planks"
    """Acacia Planks (ID: 17)"""

    ACACIA_PRESSURE_PLATE = "acacia_pressure_plate"
    """Acacia Pressure Plate (ID: 237)"""

    ACACIA_SAPLING = "acacia_sapling"
    """Acacia Sapling (ID: 27)"""

    ACACIA_SIGN = "acacia_sign"
    """Acacia Sign (ID: 189)"""

    ACACIA_SLAB = "acacia_slab"
    """Acacia Slab (ID: 543)"""

    ACACIA_STAIRS = "acacia_stairs"
    """Acacia Stairs (ID: 457)"""

    ACACIA_TRAPDOOR = "acacia_trapdoor"
    """Acacia Trapdoor (ID: 288)"""

    ACACIA_WALL_HANGING_SIGN = "acacia_wall_hanging_sign"
    """Acacia Hanging Sign (ID: 222)"""

    ACACIA_WALL_SIGN = "acacia_wall_sign"
    """Acacia Sign (ID: 202)"""

    ACACIA_WOOD = "acacia_wood"
    """Acacia Wood (ID: 70)"""

    ACTIVATOR_RAIL = "activator_rail"
    """Activator Rail (ID: 423)"""

    AIR = "air"
    """Air (ID: 0)"""

    ALLIUM = "allium"
    """Allium (ID: 151)"""

    AMETHYST_BLOCK = "amethyst_block"
    """Block of Amethyst (ID: 903)"""

    AMETHYST_CLUSTER = "amethyst_cluster"
    """Amethyst Cluster (ID: 905)"""

    ANCIENT_DEBRIS = "ancient_debris"
    """Ancient Debris (ID: 841)"""

    ANDESITE = "andesite"
    """Andesite (ID: 6)"""

    ANDESITE_SLAB = "andesite_slab"
    """Andesite Slab (ID: 755)"""

    ANDESITE_STAIRS = "andesite_stairs"
    """Andesite Stairs (ID: 742)"""

    ANDESITE_WALL = "andesite_wall"
    """Andesite Wall (ID: 767)"""

    ANVIL = "anvil"
    """Anvil (ID: 408)"""

    ATTACHED_MELON_STEM = "attached_melon_stem"
    """Attached Melon Stem (ID: 314)"""

    ATTACHED_PUMPKIN_STEM = "attached_pumpkin_stem"
    """Attached Pumpkin Stem (ID: 313)"""

    AZALEA = "azalea"
    """Azalea (ID: 1012)"""

    AZALEA_LEAVES = "azalea_leaves"
    """Azalea Leaves (ID: 90)"""

    AZURE_BLUET = "azure_bluet"
    """Azure Bluet (ID: 152)"""

    BAMBOO = "bamboo"
    """Bamboo (ID: 727)"""

    BAMBOO_BLOCK = "bamboo_block"
    """Block of Bamboo (ID: 56)"""

    BAMBOO_BUTTON = "bamboo_button"
    """Bamboo Button (ID: 393)"""

    BAMBOO_DOOR = "bamboo_door"
    """Bamboo Door (ID: 590)"""

    BAMBOO_FENCE = "bamboo_fence"
    """Bamboo Fence (ID: 582)"""

    BAMBOO_FENCE_GATE = "bamboo_fence_gate"
    """Bamboo Fence Gate (ID: 574)"""

    BAMBOO_HANGING_SIGN = "bamboo_hanging_sign"
    """Bamboo Hanging Sign (ID: 218)"""

    BAMBOO_MOSAIC = "bamboo_mosaic"
    """Bamboo Mosaic (ID: 22)"""

    BAMBOO_MOSAIC_SLAB = "bamboo_mosaic_slab"
    """Bamboo Mosaic Slab (ID: 548)"""

    BAMBOO_MOSAIC_STAIRS = "bamboo_mosaic_stairs"
    """Bamboo Mosaic Stairs (ID: 462)"""

    BAMBOO_PLANKS = "bamboo_planks"
    """Bamboo Planks (ID: 21)"""

    BAMBOO_PRESSURE_PLATE = "bamboo_pressure_plate"
    """Bamboo Pressure Plate (ID: 241)"""

    BAMBOO_SAPLING = "bamboo_sapling"
    """Bamboo Shoot (ID: 726)"""

    BAMBOO_SIGN = "bamboo_sign"
    """Bamboo Sign (ID: 194)"""

    BAMBOO_SLAB = "bamboo_slab"
    """Bamboo Slab (ID: 547)"""

    BAMBOO_STAIRS = "bamboo_stairs"
    """Bamboo Stairs (ID: 461)"""

    BAMBOO_TRAPDOOR = "bamboo_trapdoor"
    """Bamboo Trapdoor (ID: 292)"""

    BAMBOO_WALL_HANGING_SIGN = "bamboo_wall_hanging_sign"
    """Bamboo Hanging Sign (ID: 229)"""

    BAMBOO_WALL_SIGN = "bamboo_wall_sign"
    """Bamboo Sign (ID: 207)"""

    BARREL = "barrel"
    """Barrel (ID: 774)"""

    BARRIER = "barrier"
    """Barrier (ID: 464)"""

    BASALT = "basalt"
    """Basalt (ID: 258)"""

    BEACON = "beacon"
    """Beacon (ID: 352)"""

    BEDROCK = "bedrock"
    """Bedrock (ID: 31)"""

    BEE_NEST = "bee_nest"
    """Bee Nest (ID: 836)"""

    BEEHIVE = "beehive"
    """Beehive (ID: 837)"""

    BEETROOTS = "beetroots"
    """Beetroots (ID: 601)"""

    BELL = "bell"
    """Bell (ID: 783)"""

    BIG_DRIPLEAF = "big_dripleaf"
    """Big Dripleaf (ID: 1017)"""

    BIG_DRIPLEAF_STEM = "big_dripleaf_stem"
    """Big Dripleaf Stem (ID: 1018)"""

    BIRCH_BUTTON = "birch_button"
    """Birch Button (ID: 387)"""

    BIRCH_DOOR = "birch_door"
    """Birch Door (ID: 584)"""

    BIRCH_FENCE = "birch_fence"
    """Birch Fence (ID: 576)"""

    BIRCH_FENCE_GATE = "birch_fence_gate"
    """Birch Fence Gate (ID: 568)"""

    BIRCH_HANGING_SIGN = "birch_hanging_sign"
    """Birch Hanging Sign (ID: 210)"""

    BIRCH_LEAVES = "birch_leaves"
    """Birch Leaves (ID: 84)"""

    BIRCH_LOG = "birch_log"
    """Birch Log (ID: 48)"""

    BIRCH_PLANKS = "birch_planks"
    """Birch Planks (ID: 15)"""

    BIRCH_PRESSURE_PLATE = "birch_pressure_plate"
    """Birch Pressure Plate (ID: 235)"""

    BIRCH_SAPLING = "birch_sapling"
    """Birch Sapling (ID: 25)"""

    BIRCH_SIGN = "birch_sign"
    """Birch Sign (ID: 188)"""

    BIRCH_SLAB = "birch_slab"
    """Birch Slab (ID: 541)"""

    BIRCH_STAIRS = "birch_stairs"
    """Birch Stairs (ID: 349)"""

    BIRCH_TRAPDOOR = "birch_trapdoor"
    """Birch Trapdoor (ID: 286)"""

    BIRCH_WALL_HANGING_SIGN = "birch_wall_hanging_sign"
    """Birch Hanging Sign (ID: 221)"""

    BIRCH_WALL_SIGN = "birch_wall_sign"
    """Birch Sign (ID: 201)"""

    BIRCH_WOOD = "birch_wood"
    """Birch Wood (ID: 68)"""

    BLACK_BANNER = "black_banner"
    """Black Banner (ID: 518)"""

    BLACK_BED = "black_bed"
    """Black Bed (ID: 118)"""

    BLACK_CANDLE = "black_candle"
    """Black Candle (ID: 885)"""

    BLACK_CANDLE_CAKE = "black_candle_cake"
    """Cake with Black Candle (ID: 902)"""

    BLACK_CARPET = "black_carpet"
    """Black Carpet (ID: 493)"""

    BLACK_CONCRETE = "black_concrete"
    """Black Concrete (ID: 661)"""

    BLACK_CONCRETE_POWDER = "black_concrete_powder"
    """Black Concrete Powder (ID: 677)"""

    BLACK_GLAZED_TERRACOTTA = "black_glazed_terracotta"
    """Black Glazed Terracotta (ID: 645)"""

    BLACK_SHULKER_BOX = "black_shulker_box"
    """Black Shulker Box (ID: 629)"""

    BLACK_STAINED_GLASS = "black_stained_glass"
    """Black Stained Glass (ID: 283)"""

    BLACK_STAINED_GLASS_PANE = "black_stained_glass_pane"
    """Black Stained Glass Pane (ID: 456)"""

    BLACK_TERRACOTTA = "black_terracotta"
    """Black Terracotta (ID: 440)"""

    BLACK_WALL_BANNER = "black_wall_banner"
    """Black Banner (ID: 534)"""

    BLACK_WOOL = "black_wool"
    """Black Wool (ID: 145)"""

    BLACKSTONE = "blackstone"
    """Blackstone (ID: 849)"""

    BLACKSTONE_SLAB = "blackstone_slab"
    """Blackstone Slab (ID: 852)"""

    BLACKSTONE_STAIRS = "blackstone_stairs"
    """Blackstone Stairs (ID: 850)"""

    BLACKSTONE_WALL = "blackstone_wall"
    """Blackstone Wall (ID: 851)"""

    BLAST_FURNACE = "blast_furnace"
    """Blast Furnace (ID: 776)"""

    BLUE_BANNER = "blue_banner"
    """Blue Banner (ID: 514)"""

    BLUE_BED = "blue_bed"
    """Blue Bed (ID: 114)"""

    BLUE_CANDLE = "blue_candle"
    """Blue Candle (ID: 881)"""

    BLUE_CANDLE_CAKE = "blue_candle_cake"
    """Cake with Blue Candle (ID: 898)"""

    BLUE_CARPET = "blue_carpet"
    """Blue Carpet (ID: 489)"""

    BLUE_CONCRETE = "blue_concrete"
    """Blue Concrete (ID: 657)"""

    BLUE_CONCRETE_POWDER = "blue_concrete_powder"
    """Blue Concrete Powder (ID: 673)"""

    BLUE_GLAZED_TERRACOTTA = "blue_glazed_terracotta"
    """Blue Glazed Terracotta (ID: 641)"""

    BLUE_ICE = "blue_ice"
    """Blue Ice (ID: 724)"""

    BLUE_ORCHID = "blue_orchid"
    """Blue Orchid (ID: 150)"""

    BLUE_SHULKER_BOX = "blue_shulker_box"
    """Blue Shulker Box (ID: 625)"""

    BLUE_STAINED_GLASS = "blue_stained_glass"
    """Blue Stained Glass (ID: 279)"""

    BLUE_STAINED_GLASS_PANE = "blue_stained_glass_pane"
    """Blue Stained Glass Pane (ID: 452)"""

    BLUE_TERRACOTTA = "blue_terracotta"
    """Blue Terracotta (ID: 436)"""

    BLUE_WALL_BANNER = "blue_wall_banner"
    """Blue Banner (ID: 530)"""

    BLUE_WOOL = "blue_wool"
    """Blue Wool (ID: 141)"""

    BONE_BLOCK = "bone_block"
    """Bone Block (ID: 610)"""

    BOOKSHELF = "bookshelf"
    """Bookshelf (ID: 167)"""

    BRAIN_CORAL = "brain_coral"
    """Brain Coral (ID: 699)"""

    BRAIN_CORAL_BLOCK = "brain_coral_block"
    """Brain Coral Block (ID: 689)"""

    BRAIN_CORAL_FAN = "brain_coral_fan"
    """Brain Coral Fan (ID: 709)"""

    BRAIN_CORAL_WALL_FAN = "brain_coral_wall_fan"
    """Brain Coral Wall Fan (ID: 719)"""

    BREWING_STAND = "brewing_stand"
    """Brewing Stand (ID: 330)"""

    BRICK_SLAB = "brick_slab"
    """Brick Slab (ID: 555)"""

    BRICK_STAIRS = "brick_stairs"
    """Brick Stairs (ID: 320)"""

    BRICK_WALL = "brick_wall"
    """Brick Wall (ID: 759)"""

    BRICKS = "bricks"
    """Bricks (ID: 165)"""

    BROWN_BANNER = "brown_banner"
    """Brown Banner (ID: 515)"""

    BROWN_BED = "brown_bed"
    """Brown Bed (ID: 115)"""

    BROWN_CANDLE = "brown_candle"
    """Brown Candle (ID: 882)"""

    BROWN_CANDLE_CAKE = "brown_candle_cake"
    """Cake with Brown Candle (ID: 899)"""

    BROWN_CARPET = "brown_carpet"
    """Brown Carpet (ID: 490)"""

    BROWN_CONCRETE = "brown_concrete"
    """Brown Concrete (ID: 658)"""

    BROWN_CONCRETE_POWDER = "brown_concrete_powder"
    """Brown Concrete Powder (ID: 674)"""

    BROWN_GLAZED_TERRACOTTA = "brown_glazed_terracotta"
    """Brown Glazed Terracotta (ID: 642)"""

    BROWN_MUSHROOM = "brown_mushroom"
    """Brown Mushroom (ID: 161)"""

    BROWN_MUSHROOM_BLOCK = "brown_mushroom_block"
    """Brown Mushroom Block (ID: 305)"""

    BROWN_SHULKER_BOX = "brown_shulker_box"
    """Brown Shulker Box (ID: 626)"""

    BROWN_STAINED_GLASS = "brown_stained_glass"
    """Brown Stained Glass (ID: 280)"""

    BROWN_STAINED_GLASS_PANE = "brown_stained_glass_pane"
    """Brown Stained Glass Pane (ID: 453)"""

    BROWN_TERRACOTTA = "brown_terracotta"
    """Brown Terracotta (ID: 437)"""

    BROWN_WALL_BANNER = "brown_wall_banner"
    """Brown Banner (ID: 531)"""

    BROWN_WOOL = "brown_wool"
    """Brown Wool (ID: 142)"""

    BUBBLE_COLUMN = "bubble_column"
    """Bubble Column (ID: 731)"""

    BUBBLE_CORAL = "bubble_coral"
    """Bubble Coral (ID: 700)"""

    BUBBLE_CORAL_BLOCK = "bubble_coral_block"
    """Bubble Coral Block (ID: 690)"""

    BUBBLE_CORAL_FAN = "bubble_coral_fan"
    """Bubble Coral Fan (ID: 710)"""

    BUBBLE_CORAL_WALL_FAN = "bubble_coral_wall_fan"
    """Bubble Coral Wall Fan (ID: 720)"""

    BUDDING_AMETHYST = "budding_amethyst"
    """Budding Amethyst (ID: 904)"""

    CACTUS = "cactus"
    """Cactus (ID: 250)"""

    CAKE = "cake"
    """Cake (ID: 266)"""

    CALCITE = "calcite"
    """Calcite (ID: 923)"""

    CALIBRATED_SCULK_SENSOR = "calibrated_sculk_sensor"
    """Calibrated Sculk Sensor (ID: 927)"""

    CAMPFIRE = "campfire"
    """Campfire (ID: 786)"""

    CANDLE = "candle"
    """Candle (ID: 869)"""

    CANDLE_CAKE = "candle_cake"
    """Cake with Candle (ID: 886)"""

    CARROTS = "carrots"
    """Carrots (ID: 383)"""

    CARTOGRAPHY_TABLE = "cartography_table"
    """Cartography Table (ID: 777)"""

    CARVED_PUMPKIN = "carved_pumpkin"
    """Carved Pumpkin (ID: 264)"""

    CAULDRON = "cauldron"
    """Cauldron (ID: 331)"""

    CAVE_AIR = "cave_air"
    """Cave Air (ID: 730)"""

    CAVE_VINES = "cave_vines"
    """Cave Vines (ID: 1009)"""

    CAVE_VINES_PLANT = "cave_vines_plant"
    """Cave Vines Plant (ID: 1010)"""

    CHAIN = "chain"
    """Chain (ID: 309)"""

    CHAIN_COMMAND_BLOCK = "chain_command_block"
    """Chain Command Block (ID: 605)"""

    CHERRY_BUTTON = "cherry_button"
    """Cherry Button (ID: 390)"""

    CHERRY_DOOR = "cherry_door"
    """Cherry Door (ID: 587)"""

    CHERRY_FENCE = "cherry_fence"
    """Cherry Fence (ID: 579)"""

    CHERRY_FENCE_GATE = "cherry_fence_gate"
    """Cherry Fence Gate (ID: 571)"""

    CHERRY_HANGING_SIGN = "cherry_hanging_sign"
    """Cherry Hanging Sign (ID: 212)"""

    CHERRY_LEAVES = "cherry_leaves"
    """Cherry Leaves (ID: 87)"""

    CHERRY_LOG = "cherry_log"
    """Cherry Log (ID: 51)"""

    CHERRY_PLANKS = "cherry_planks"
    """Cherry Planks (ID: 18)"""

    CHERRY_PRESSURE_PLATE = "cherry_pressure_plate"
    """Cherry Pressure Plate (ID: 238)"""

    CHERRY_SAPLING = "cherry_sapling"
    """Cherry Sapling (ID: 28)"""

    CHERRY_SIGN = "cherry_sign"
    """Cherry Sign (ID: 190)"""

    CHERRY_SLAB = "cherry_slab"
    """Cherry Slab (ID: 544)"""

    CHERRY_STAIRS = "cherry_stairs"
    """Cherry Stairs (ID: 458)"""

    CHERRY_TRAPDOOR = "cherry_trapdoor"
    """Cherry Trapdoor (ID: 289)"""

    CHERRY_WALL_HANGING_SIGN = "cherry_wall_hanging_sign"
    """Cherry Hanging Sign (ID: 223)"""

    CHERRY_WALL_SIGN = "cherry_wall_sign"
    """Cherry Sign (ID: 203)"""

    CHERRY_WOOD = "cherry_wood"
    """Cherry Wood (ID: 71)"""

    CHEST = "chest"
    """Chest (ID: 177)"""

    CHIPPED_ANVIL = "chipped_anvil"
    """Chipped Anvil (ID: 409)"""

    CHISELED_BOOKSHELF = "chiseled_bookshelf"
    """Chiseled Bookshelf (ID: 168)"""

    CHISELED_COPPER = "chiseled_copper"
    """Chiseled Copper (ID: 945)"""

    CHISELED_DEEPSLATE = "chiseled_deepslate"
    """Chiseled Deepslate (ID: 1040)"""

    CHISELED_NETHER_BRICKS = "chiseled_nether_bricks"
    """Chiseled Nether Bricks (ID: 866)"""

    CHISELED_POLISHED_BLACKSTONE = "chiseled_polished_blackstone"
    """Chiseled Polished Blackstone (ID: 856)"""

    CHISELED_QUARTZ_BLOCK = "chiseled_quartz_block"
    """Chiseled Quartz Block (ID: 420)"""

    CHISELED_RED_SANDSTONE = "chiseled_red_sandstone"
    """Chiseled Red Sandstone (ID: 536)"""

    CHISELED_SANDSTONE = "chiseled_sandstone"
    """Chiseled Sandstone (ID: 100)"""

    CHISELED_STONE_BRICKS = "chiseled_stone_bricks"
    """Chiseled Stone Bricks (ID: 296)"""

    CHISELED_TUFF = "chiseled_tuff"
    """Chiseled Tuff (ID: 917)"""

    CHISELED_TUFF_BRICKS = "chiseled_tuff_bricks"
    """Chiseled Tuff Bricks (ID: 922)"""

    CHORUS_FLOWER = "chorus_flower"
    """Chorus Flower (ID: 593)"""

    CHORUS_PLANT = "chorus_plant"
    """Chorus Plant (ID: 592)"""

    CLAY = "clay"
    """Clay (ID: 251)"""

    COAL_BLOCK = "coal_block"
    """Block of Coal (ID: 495)"""

    COAL_ORE = "coal_ore"
    """Coal Ore (ID: 43)"""

    COARSE_DIRT = "coarse_dirt"
    """Coarse Dirt (ID: 10)"""

    COBBLED_DEEPSLATE = "cobbled_deepslate"
    """Cobbled Deepslate (ID: 1024)"""

    COBBLED_DEEPSLATE_SLAB = "cobbled_deepslate_slab"
    """Cobbled Deepslate Slab (ID: 1026)"""

    COBBLED_DEEPSLATE_STAIRS = "cobbled_deepslate_stairs"
    """Cobbled Deepslate Stairs (ID: 1025)"""

    COBBLED_DEEPSLATE_WALL = "cobbled_deepslate_wall"
    """Cobbled Deepslate Wall (ID: 1027)"""

    COBBLESTONE = "cobblestone"
    """Cobblestone (ID: 12)"""

    COBBLESTONE_SLAB = "cobblestone_slab"
    """Cobblestone Slab (ID: 554)"""

    COBBLESTONE_STAIRS = "cobblestone_stairs"
    """Cobblestone Stairs (ID: 198)"""

    COBBLESTONE_WALL = "cobblestone_wall"
    """Cobblestone Wall (ID: 353)"""

    COBWEB = "cobweb"
    """Cobweb (ID: 122)"""

    COCOA = "cocoa"
    """Cocoa (ID: 340)"""

    COMMAND_BLOCK = "command_block"
    """Command Block (ID: 351)"""

    COMPARATOR = "comparator"
    """Redstone Comparator (ID: 414)"""

    COMPOSTER = "composter"
    """Composter (ID: 834)"""

    CONDUIT = "conduit"
    """Conduit (ID: 725)"""

    COPPER_BLOCK = "copper_block"
    """Block of Copper (ID: 932)"""

    COPPER_BULB = "copper_bulb"
    """Copper Bulb (ID: 998)"""

    COPPER_DOOR = "copper_door"
    """Copper Door (ID: 974)"""

    COPPER_GRATE = "copper_grate"
    """Copper Grate (ID: 990)"""

    COPPER_ORE = "copper_ore"
    """Copper Ore (ID: 936)"""

    COPPER_TRAPDOOR = "copper_trapdoor"
    """Copper Trapdoor (ID: 982)"""

    CORNFLOWER = "cornflower"
    """Cornflower (ID: 158)"""

    CRACKED_DEEPSLATE_BRICKS = "cracked_deepslate_bricks"
    """Cracked Deepslate Bricks (ID: 1041)"""

    CRACKED_DEEPSLATE_TILES = "cracked_deepslate_tiles"
    """Cracked Deepslate Tiles (ID: 1042)"""

    CRACKED_NETHER_BRICKS = "cracked_nether_bricks"
    """Cracked Nether Bricks (ID: 867)"""

    CRACKED_POLISHED_BLACKSTONE_BRICKS = "cracked_polished_blackstone_bricks"
    """Cracked Polished Blackstone Bricks (ID: 855)"""

    CRACKED_STONE_BRICKS = "cracked_stone_bricks"
    """Cracked Stone Bricks (ID: 295)"""

    CRAFTER = "crafter"
    """Crafter (ID: 1056)"""

    CRAFTING_TABLE = "crafting_table"
    """Crafting Table (ID: 182)"""

    CREEPER_HEAD = "creeper_head"
    """Creeper Head (ID: 402)"""

    CREEPER_WALL_HEAD = "creeper_wall_head"
    """Creeper Head (ID: 403)"""

    CRIMSON_BUTTON = "crimson_button"
    """Crimson Button (ID: 824)"""

    CRIMSON_DOOR = "crimson_door"
    """Crimson Door (ID: 826)"""

    CRIMSON_FENCE = "crimson_fence"
    """Crimson Fence (ID: 816)"""

    CRIMSON_FENCE_GATE = "crimson_fence_gate"
    """Crimson Fence Gate (ID: 820)"""

    CRIMSON_FUNGUS = "crimson_fungus"
    """Crimson Fungus (ID: 803)"""

    CRIMSON_HANGING_SIGN = "crimson_hanging_sign"
    """Crimson Hanging Sign (ID: 215)"""

    CRIMSON_HYPHAE = "crimson_hyphae"
    """Crimson Hyphae (ID: 800)"""

    CRIMSON_NYLIUM = "crimson_nylium"
    """Crimson Nylium (ID: 802)"""

    CRIMSON_PLANKS = "crimson_planks"
    """Crimson Planks (ID: 810)"""

    CRIMSON_PRESSURE_PLATE = "crimson_pressure_plate"
    """Crimson Pressure Plate (ID: 814)"""

    CRIMSON_ROOTS = "crimson_roots"
    """Crimson Roots (ID: 809)"""

    CRIMSON_SIGN = "crimson_sign"
    """Crimson Sign (ID: 828)"""

    CRIMSON_SLAB = "crimson_slab"
    """Crimson Slab (ID: 812)"""

    CRIMSON_STAIRS = "crimson_stairs"
    """Crimson Stairs (ID: 822)"""

    CRIMSON_STEM = "crimson_stem"
    """Crimson Stem (ID: 798)"""

    CRIMSON_TRAPDOOR = "crimson_trapdoor"
    """Crimson Trapdoor (ID: 818)"""

    CRIMSON_WALL_HANGING_SIGN = "crimson_wall_hanging_sign"
    """Crimson Hanging Sign (ID: 227)"""

    CRIMSON_WALL_SIGN = "crimson_wall_sign"
    """Crimson Sign (ID: 830)"""

    CRYING_OBSIDIAN = "crying_obsidian"
    """Crying Obsidian (ID: 842)"""

    CUT_COPPER = "cut_copper"
    """Cut Copper (ID: 941)"""

    CUT_COPPER_SLAB = "cut_copper_slab"
    """Cut Copper Slab (ID: 957)"""

    CUT_COPPER_STAIRS = "cut_copper_stairs"
    """Cut Copper Stairs (ID: 953)"""

    CUT_RED_SANDSTONE = "cut_red_sandstone"
    """Cut Red Sandstone (ID: 537)"""

    CUT_RED_SANDSTONE_SLAB = "cut_red_sandstone_slab"
    """Cut Red Sandstone Slab (ID: 561)"""

    CUT_SANDSTONE = "cut_sandstone"
    """Cut Sandstone (ID: 101)"""

    CUT_SANDSTONE_SLAB = "cut_sandstone_slab"
    """Cut Sandstone Slab (ID: 552)"""

    CYAN_BANNER = "cyan_banner"
    """Cyan Banner (ID: 512)"""

    CYAN_BED = "cyan_bed"
    """Cyan Bed (ID: 112)"""

    CYAN_CANDLE = "cyan_candle"
    """Cyan Candle (ID: 879)"""

    CYAN_CANDLE_CAKE = "cyan_candle_cake"
    """Cake with Cyan Candle (ID: 896)"""

    CYAN_CARPET = "cyan_carpet"
    """Cyan Carpet (ID: 487)"""

    CYAN_CONCRETE = "cyan_concrete"
    """Cyan Concrete (ID: 655)"""

    CYAN_CONCRETE_POWDER = "cyan_concrete_powder"
    """Cyan Concrete Powder (ID: 671)"""

    CYAN_GLAZED_TERRACOTTA = "cyan_glazed_terracotta"
    """Cyan Glazed Terracotta (ID: 639)"""

    CYAN_SHULKER_BOX = "cyan_shulker_box"
    """Cyan Shulker Box (ID: 623)"""

    CYAN_STAINED_GLASS = "cyan_stained_glass"
    """Cyan Stained Glass (ID: 277)"""

    CYAN_STAINED_GLASS_PANE = "cyan_stained_glass_pane"
    """Cyan Stained Glass Pane (ID: 450)"""

    CYAN_TERRACOTTA = "cyan_terracotta"
    """Cyan Terracotta (ID: 434)"""

    CYAN_WALL_BANNER = "cyan_wall_banner"
    """Cyan Banner (ID: 528)"""

    CYAN_WOOL = "cyan_wool"
    """Cyan Wool (ID: 139)"""

    DAMAGED_ANVIL = "damaged_anvil"
    """Damaged Anvil (ID: 410)"""

    DANDELION = "dandelion"
    """Dandelion (ID: 147)"""

    DARK_OAK_BUTTON = "dark_oak_button"
    """Dark Oak Button (ID: 391)"""

    DARK_OAK_DOOR = "dark_oak_door"
    """Dark Oak Door (ID: 588)"""

    DARK_OAK_FENCE = "dark_oak_fence"
    """Dark Oak Fence (ID: 580)"""

    DARK_OAK_FENCE_GATE = "dark_oak_fence_gate"
    """Dark Oak Fence Gate (ID: 572)"""

    DARK_OAK_HANGING_SIGN = "dark_oak_hanging_sign"
    """Dark Oak Hanging Sign (ID: 214)"""

    DARK_OAK_LEAVES = "dark_oak_leaves"
    """Dark Oak Leaves (ID: 88)"""

    DARK_OAK_LOG = "dark_oak_log"
    """Dark Oak Log (ID: 52)"""

    DARK_OAK_PLANKS = "dark_oak_planks"
    """Dark Oak Planks (ID: 19)"""

    DARK_OAK_PRESSURE_PLATE = "dark_oak_pressure_plate"
    """Dark Oak Pressure Plate (ID: 239)"""

    DARK_OAK_SAPLING = "dark_oak_sapling"
    """Dark Oak Sapling (ID: 29)"""

    DARK_OAK_SIGN = "dark_oak_sign"
    """Dark Oak Sign (ID: 192)"""

    DARK_OAK_SLAB = "dark_oak_slab"
    """Dark Oak Slab (ID: 545)"""

    DARK_OAK_STAIRS = "dark_oak_stairs"
    """Dark Oak Stairs (ID: 459)"""

    DARK_OAK_TRAPDOOR = "dark_oak_trapdoor"
    """Dark Oak Trapdoor (ID: 290)"""

    DARK_OAK_WALL_HANGING_SIGN = "dark_oak_wall_hanging_sign"
    """Dark Oak Hanging Sign (ID: 225)"""

    DARK_OAK_WALL_SIGN = "dark_oak_wall_sign"
    """Dark Oak Sign (ID: 205)"""

    DARK_OAK_WOOD = "dark_oak_wood"
    """Dark Oak Wood (ID: 72)"""

    DARK_PRISMARINE = "dark_prismarine"
    """Dark Prismarine (ID: 469)"""

    DARK_PRISMARINE_SLAB = "dark_prismarine_slab"
    """Dark Prismarine Slab (ID: 475)"""

    DARK_PRISMARINE_STAIRS = "dark_prismarine_stairs"
    """Dark Prismarine Stairs (ID: 472)"""

    DAYLIGHT_DETECTOR = "daylight_detector"
    """Daylight Detector (ID: 415)"""

    DEAD_BRAIN_CORAL = "dead_brain_coral"
    """Dead Brain Coral (ID: 694)"""

    DEAD_BRAIN_CORAL_BLOCK = "dead_brain_coral_block"
    """Dead Brain Coral Block (ID: 684)"""

    DEAD_BRAIN_CORAL_FAN = "dead_brain_coral_fan"
    """Dead Brain Coral Fan (ID: 704)"""

    DEAD_BRAIN_CORAL_WALL_FAN = "dead_brain_coral_wall_fan"
    """Dead Brain Coral Wall Fan (ID: 714)"""

    DEAD_BUBBLE_CORAL = "dead_bubble_coral"
    """Dead Bubble Coral (ID: 695)"""

    DEAD_BUBBLE_CORAL_BLOCK = "dead_bubble_coral_block"
    """Dead Bubble Coral Block (ID: 685)"""

    DEAD_BUBBLE_CORAL_FAN = "dead_bubble_coral_fan"
    """Dead Bubble Coral Fan (ID: 705)"""

    DEAD_BUBBLE_CORAL_WALL_FAN = "dead_bubble_coral_wall_fan"
    """Dead Bubble Coral Wall Fan (ID: 715)"""

    DEAD_BUSH = "dead_bush"
    """Dead Bush (ID: 125)"""

    DEAD_FIRE_CORAL = "dead_fire_coral"
    """Dead Fire Coral (ID: 696)"""

    DEAD_FIRE_CORAL_BLOCK = "dead_fire_coral_block"
    """Dead Fire Coral Block (ID: 686)"""

    DEAD_FIRE_CORAL_FAN = "dead_fire_coral_fan"
    """Dead Fire Coral Fan (ID: 706)"""

    DEAD_FIRE_CORAL_WALL_FAN = "dead_fire_coral_wall_fan"
    """Dead Fire Coral Wall Fan (ID: 716)"""

    DEAD_HORN_CORAL = "dead_horn_coral"
    """Dead Horn Coral (ID: 697)"""

    DEAD_HORN_CORAL_BLOCK = "dead_horn_coral_block"
    """Dead Horn Coral Block (ID: 687)"""

    DEAD_HORN_CORAL_FAN = "dead_horn_coral_fan"
    """Dead Horn Coral Fan (ID: 707)"""

    DEAD_HORN_CORAL_WALL_FAN = "dead_horn_coral_wall_fan"
    """Dead Horn Coral Wall Fan (ID: 717)"""

    DEAD_TUBE_CORAL = "dead_tube_coral"
    """Dead Tube Coral (ID: 693)"""

    DEAD_TUBE_CORAL_BLOCK = "dead_tube_coral_block"
    """Dead Tube Coral Block (ID: 683)"""

    DEAD_TUBE_CORAL_FAN = "dead_tube_coral_fan"
    """Dead Tube Coral Fan (ID: 703)"""

    DEAD_TUBE_CORAL_WALL_FAN = "dead_tube_coral_wall_fan"
    """Dead Tube Coral Wall Fan (ID: 713)"""

    DECORATED_POT = "decorated_pot"
    """Decorated Pot (ID: 1055)"""

    DEEPSLATE = "deepslate"
    """Deepslate (ID: 1023)"""

    DEEPSLATE_BRICK_SLAB = "deepslate_brick_slab"
    """Deepslate Brick Slab (ID: 1038)"""

    DEEPSLATE_BRICK_STAIRS = "deepslate_brick_stairs"
    """Deepslate Brick Stairs (ID: 1037)"""

    DEEPSLATE_BRICK_WALL = "deepslate_brick_wall"
    """Deepslate Brick Wall (ID: 1039)"""

    DEEPSLATE_BRICKS = "deepslate_bricks"
    """Deepslate Bricks (ID: 1036)"""

    DEEPSLATE_COAL_ORE = "deepslate_coal_ore"
    """Deepslate Coal Ore (ID: 44)"""

    DEEPSLATE_COPPER_ORE = "deepslate_copper_ore"
    """Deepslate Copper Ore (ID: 937)"""

    DEEPSLATE_DIAMOND_ORE = "deepslate_diamond_ore"
    """Deepslate Diamond Ore (ID: 180)"""

    DEEPSLATE_EMERALD_ORE = "deepslate_emerald_ore"
    """Deepslate Emerald Ore (ID: 343)"""

    DEEPSLATE_GOLD_ORE = "deepslate_gold_ore"
    """Deepslate Gold Ore (ID: 40)"""

    DEEPSLATE_IRON_ORE = "deepslate_iron_ore"
    """Deepslate Iron Ore (ID: 42)"""

    DEEPSLATE_LAPIS_ORE = "deepslate_lapis_ore"
    """Deepslate Lapis Lazuli Ore (ID: 96)"""

    DEEPSLATE_REDSTONE_ORE = "deepslate_redstone_ore"
    """Deepslate Redstone Ore (ID: 243)"""

    DEEPSLATE_TILE_SLAB = "deepslate_tile_slab"
    """Deepslate Tile Slab (ID: 1034)"""

    DEEPSLATE_TILE_STAIRS = "deepslate_tile_stairs"
    """Deepslate Tile Stairs (ID: 1033)"""

    DEEPSLATE_TILE_WALL = "deepslate_tile_wall"
    """Deepslate Tile Wall (ID: 1035)"""

    DEEPSLATE_TILES = "deepslate_tiles"
    """Deepslate Tiles (ID: 1032)"""

    DETECTOR_RAIL = "detector_rail"
    """Detector Rail (ID: 120)"""

    DIAMOND_BLOCK = "diamond_block"
    """Block of Diamond (ID: 181)"""

    DIAMOND_ORE = "diamond_ore"
    """Diamond Ore (ID: 179)"""

    DIORITE = "diorite"
    """Diorite (ID: 4)"""

    DIORITE_SLAB = "diorite_slab"
    """Diorite Slab (ID: 758)"""

    DIORITE_STAIRS = "diorite_stairs"
    """Diorite Stairs (ID: 745)"""

    DIORITE_WALL = "diorite_wall"
    """Diorite Wall (ID: 771)"""

    DIRT = "dirt"
    """Dirt (ID: 9)"""

    DIRT_PATH = "dirt_path"
    """Dirt Path (ID: 602)"""

    DISPENSER = "dispenser"
    """Dispenser (ID: 98)"""

    DRAGON_EGG = "dragon_egg"
    """Dragon Egg (ID: 338)"""

    DRAGON_HEAD = "dragon_head"
    """Dragon Head (ID: 404)"""

    DRAGON_WALL_HEAD = "dragon_wall_head"
    """Dragon Head (ID: 405)"""

    DRIED_KELP_BLOCK = "dried_kelp_block"
    """Dried Kelp Block (ID: 680)"""

    DRIPSTONE_BLOCK = "dripstone_block"
    """Dripstone Block (ID: 1008)"""

    DROPPER = "dropper"
    """Dropper (ID: 424)"""

    EMERALD_BLOCK = "emerald_block"
    """Block of Emerald (ID: 347)"""

    EMERALD_ORE = "emerald_ore"
    """Emerald Ore (ID: 342)"""

    ENCHANTING_TABLE = "enchanting_table"
    """Enchanting Table (ID: 329)"""

    END_GATEWAY = "end_gateway"
    """End Gateway (ID: 603)"""

    END_PORTAL = "end_portal"
    """End Portal (ID: 335)"""

    END_PORTAL_FRAME = "end_portal_frame"
    """End Portal Frame (ID: 336)"""

    END_ROD = "end_rod"
    """End Rod (ID: 591)"""

    END_STONE = "end_stone"
    """End Stone (ID: 337)"""

    END_STONE_BRICK_SLAB = "end_stone_brick_slab"
    """End Stone Brick Slab (ID: 751)"""

    END_STONE_BRICK_STAIRS = "end_stone_brick_stairs"
    """End Stone Brick Stairs (ID: 737)"""

    END_STONE_BRICK_WALL = "end_stone_brick_wall"
    """End Stone Brick Wall (ID: 770)"""

    END_STONE_BRICKS = "end_stone_bricks"
    """End Stone Bricks (ID: 597)"""

    ENDER_CHEST = "ender_chest"
    """Ender Chest (ID: 344)"""

    EXPOSED_CHISELED_COPPER = "exposed_chiseled_copper"
    """Exposed Chiseled Copper (ID: 944)"""

    EXPOSED_COPPER = "exposed_copper"
    """Exposed Copper (ID: 933)"""

    EXPOSED_COPPER_BULB = "exposed_copper_bulb"
    """Exposed Copper Bulb (ID: 999)"""

    EXPOSED_COPPER_DOOR = "exposed_copper_door"
    """Exposed Copper Door (ID: 975)"""

    EXPOSED_COPPER_GRATE = "exposed_copper_grate"
    """Exposed Copper Grate (ID: 991)"""

    EXPOSED_COPPER_TRAPDOOR = "exposed_copper_trapdoor"
    """Exposed Copper Trapdoor (ID: 983)"""

    EXPOSED_CUT_COPPER = "exposed_cut_copper"
    """Exposed Cut Copper (ID: 940)"""

    EXPOSED_CUT_COPPER_SLAB = "exposed_cut_copper_slab"
    """Exposed Cut Copper Slab (ID: 956)"""

    EXPOSED_CUT_COPPER_STAIRS = "exposed_cut_copper_stairs"
    """Exposed Cut Copper Stairs (ID: 952)"""

    FARMLAND = "farmland"
    """Farmland (ID: 184)"""

    FERN = "fern"
    """Fern (ID: 124)"""

    FIRE = "fire"
    """Fire (ID: 173)"""

    FIRE_CORAL = "fire_coral"
    """Fire Coral (ID: 701)"""

    FIRE_CORAL_BLOCK = "fire_coral_block"
    """Fire Coral Block (ID: 691)"""

    FIRE_CORAL_FAN = "fire_coral_fan"
    """Fire Coral Fan (ID: 711)"""

    FIRE_CORAL_WALL_FAN = "fire_coral_wall_fan"
    """Fire Coral Wall Fan (ID: 721)"""

    FLETCHING_TABLE = "fletching_table"
    """Fletching Table (ID: 778)"""

    FLOWER_POT = "flower_pot"
    """Flower Pot (ID: 355)"""

    FLOWERING_AZALEA = "flowering_azalea"
    """Flowering Azalea (ID: 1013)"""

    FLOWERING_AZALEA_LEAVES = "flowering_azalea_leaves"
    """Flowering Azalea Leaves (ID: 91)"""

    FROGSPAWN = "frogspawn"
    """Frogspawn (ID: 1053)"""

    FROSTED_ICE = "frosted_ice"
    """Frosted Ice (ID: 606)"""

    FURNACE = "furnace"
    """Furnace (ID: 185)"""

    GILDED_BLACKSTONE = "gilded_blackstone"
    """Gilded Blackstone (ID: 860)"""

    GLASS = "glass"
    """Glass (ID: 94)"""

    GLASS_PANE = "glass_pane"
    """Glass Pane (ID: 310)"""

    GLOW_LICHEN = "glow_lichen"
    """Glow Lichen (ID: 318)"""

    GLOWSTONE = "glowstone"
    """Glowstone (ID: 262)"""

    GOLD_BLOCK = "gold_block"
    """Block of Gold (ID: 163)"""

    GOLD_ORE = "gold_ore"
    """Gold Ore (ID: 39)"""

    GRANITE = "granite"
    """Granite (ID: 2)"""

    GRANITE_SLAB = "granite_slab"
    """Granite Slab (ID: 754)"""

    GRANITE_STAIRS = "granite_stairs"
    """Granite Stairs (ID: 741)"""

    GRANITE_WALL = "granite_wall"
    """Granite Wall (ID: 763)"""

    GRASS_BLOCK = "grass_block"
    """Grass Block (ID: 8)"""

    GRAVEL = "gravel"
    """Gravel (ID: 37)"""

    GRAY_BANNER = "gray_banner"
    """Gray Banner (ID: 510)"""

    GRAY_BED = "gray_bed"
    """Gray Bed (ID: 110)"""

    GRAY_CANDLE = "gray_candle"
    """Gray Candle (ID: 877)"""

    GRAY_CANDLE_CAKE = "gray_candle_cake"
    """Cake with Gray Candle (ID: 894)"""

    GRAY_CARPET = "gray_carpet"
    """Gray Carpet (ID: 485)"""

    GRAY_CONCRETE = "gray_concrete"
    """Gray Concrete (ID: 653)"""

    GRAY_CONCRETE_POWDER = "gray_concrete_powder"
    """Gray Concrete Powder (ID: 669)"""

    GRAY_GLAZED_TERRACOTTA = "gray_glazed_terracotta"
    """Gray Glazed Terracotta (ID: 637)"""

    GRAY_SHULKER_BOX = "gray_shulker_box"
    """Gray Shulker Box (ID: 621)"""

    GRAY_STAINED_GLASS = "gray_stained_glass"
    """Gray Stained Glass (ID: 275)"""

    GRAY_STAINED_GLASS_PANE = "gray_stained_glass_pane"
    """Gray Stained Glass Pane (ID: 448)"""

    GRAY_TERRACOTTA = "gray_terracotta"
    """Gray Terracotta (ID: 432)"""

    GRAY_WALL_BANNER = "gray_wall_banner"
    """Gray Banner (ID: 526)"""

    GRAY_WOOL = "gray_wool"
    """Gray Wool (ID: 137)"""

    GREEN_BANNER = "green_banner"
    """Green Banner (ID: 516)"""

    GREEN_BED = "green_bed"
    """Green Bed (ID: 116)"""

    GREEN_CANDLE = "green_candle"
    """Green Candle (ID: 883)"""

    GREEN_CANDLE_CAKE = "green_candle_cake"
    """Cake with Green Candle (ID: 900)"""

    GREEN_CARPET = "green_carpet"
    """Green Carpet (ID: 491)"""

    GREEN_CONCRETE = "green_concrete"
    """Green Concrete (ID: 659)"""

    GREEN_CONCRETE_POWDER = "green_concrete_powder"
    """Green Concrete Powder (ID: 675)"""

    GREEN_GLAZED_TERRACOTTA = "green_glazed_terracotta"
    """Green Glazed Terracotta (ID: 643)"""

    GREEN_SHULKER_BOX = "green_shulker_box"
    """Green Shulker Box (ID: 627)"""

    GREEN_STAINED_GLASS = "green_stained_glass"
    """Green Stained Glass (ID: 281)"""

    GREEN_STAINED_GLASS_PANE = "green_stained_glass_pane"
    """Green Stained Glass Pane (ID: 454)"""

    GREEN_TERRACOTTA = "green_terracotta"
    """Green Terracotta (ID: 438)"""

    GREEN_WALL_BANNER = "green_wall_banner"
    """Green Banner (ID: 532)"""

    GREEN_WOOL = "green_wool"
    """Green Wool (ID: 143)"""

    GRINDSTONE = "grindstone"
    """Grindstone (ID: 779)"""

    HANGING_ROOTS = "hanging_roots"
    """Hanging Roots (ID: 1020)"""

    HAY_BLOCK = "hay_block"
    """Hay Bale (ID: 477)"""

    HEAVY_WEIGHTED_PRESSURE_PLATE = "heavy_weighted_pressure_plate"
    """Heavy Weighted Pressure Plate (ID: 413)"""

    HONEY_BLOCK = "honey_block"
    """Honey Block (ID: 838)"""

    HONEYCOMB_BLOCK = "honeycomb_block"
    """Honeycomb Block (ID: 839)"""

    HOPPER = "hopper"
    """Hopper (ID: 418)"""

    HORN_CORAL = "horn_coral"
    """Horn Coral (ID: 702)"""

    HORN_CORAL_BLOCK = "horn_coral_block"
    """Horn Coral Block (ID: 692)"""

    HORN_CORAL_FAN = "horn_coral_fan"
    """Horn Coral Fan (ID: 712)"""

    HORN_CORAL_WALL_FAN = "horn_coral_wall_fan"
    """Horn Coral Wall Fan (ID: 722)"""

    ICE = "ice"
    """Ice (ID: 248)"""

    INFESTED_CHISELED_STONE_BRICKS = "infested_chiseled_stone_bricks"
    """Infested Chiseled Stone Bricks (ID: 304)"""

    INFESTED_COBBLESTONE = "infested_cobblestone"
    """Infested Cobblestone (ID: 300)"""

    INFESTED_CRACKED_STONE_BRICKS = "infested_cracked_stone_bricks"
    """Infested Cracked Stone Bricks (ID: 303)"""

    INFESTED_DEEPSLATE = "infested_deepslate"
    """Infested Deepslate (ID: 1043)"""

    INFESTED_MOSSY_STONE_BRICKS = "infested_mossy_stone_bricks"
    """Infested Mossy Stone Bricks (ID: 302)"""

    INFESTED_STONE = "infested_stone"
    """Infested Stone (ID: 299)"""

    INFESTED_STONE_BRICKS = "infested_stone_bricks"
    """Infested Stone Bricks (ID: 301)"""

    IRON_BARS = "iron_bars"
    """Iron Bars (ID: 308)"""

    IRON_BLOCK = "iron_block"
    """Block of Iron (ID: 164)"""

    IRON_DOOR = "iron_door"
    """Iron Door (ID: 232)"""

    IRON_ORE = "iron_ore"
    """Iron Ore (ID: 41)"""

    IRON_TRAPDOOR = "iron_trapdoor"
    """Iron Trapdoor (ID: 466)"""

    JACK_O_LANTERN = "jack_o_lantern"
    """Jack o'Lantern (ID: 265)"""

    JIGSAW = "jigsaw"
    """Jigsaw Block (ID: 833)"""

    JUKEBOX = "jukebox"
    """Jukebox (ID: 253)"""

    JUNGLE_BUTTON = "jungle_button"
    """Jungle Button (ID: 388)"""

    JUNGLE_DOOR = "jungle_door"
    """Jungle Door (ID: 585)"""

    JUNGLE_FENCE = "jungle_fence"
    """Jungle Fence (ID: 577)"""

    JUNGLE_FENCE_GATE = "jungle_fence_gate"
    """Jungle Fence Gate (ID: 569)"""

    JUNGLE_HANGING_SIGN = "jungle_hanging_sign"
    """Jungle Hanging Sign (ID: 213)"""

    JUNGLE_LEAVES = "jungle_leaves"
    """Jungle Leaves (ID: 85)"""

    JUNGLE_LOG = "jungle_log"
    """Jungle Log (ID: 49)"""

    JUNGLE_PLANKS = "jungle_planks"
    """Jungle Planks (ID: 16)"""

    JUNGLE_PRESSURE_PLATE = "jungle_pressure_plate"
    """Jungle Pressure Plate (ID: 236)"""

    JUNGLE_SAPLING = "jungle_sapling"
    """Jungle Sapling (ID: 26)"""

    JUNGLE_SIGN = "jungle_sign"
    """Jungle Sign (ID: 191)"""

    JUNGLE_SLAB = "jungle_slab"
    """Jungle Slab (ID: 542)"""

    JUNGLE_STAIRS = "jungle_stairs"
    """Jungle Stairs (ID: 350)"""

    JUNGLE_TRAPDOOR = "jungle_trapdoor"
    """Jungle Trapdoor (ID: 287)"""

    JUNGLE_WALL_HANGING_SIGN = "jungle_wall_hanging_sign"
    """Jungle Hanging Sign (ID: 224)"""

    JUNGLE_WALL_SIGN = "jungle_wall_sign"
    """Jungle Sign (ID: 204)"""

    JUNGLE_WOOD = "jungle_wood"
    """Jungle Wood (ID: 69)"""

    KELP = "kelp"
    """Kelp (ID: 678)"""

    KELP_PLANT = "kelp_plant"
    """Kelp Plant (ID: 679)"""

    LADDER = "ladder"
    """Ladder (ID: 196)"""

    LANTERN = "lantern"
    """Lantern (ID: 784)"""

    LAPIS_BLOCK = "lapis_block"
    """Block of Lapis Lazuli (ID: 97)"""

    LAPIS_ORE = "lapis_ore"
    """Lapis Lazuli Ore (ID: 95)"""

    LARGE_AMETHYST_BUD = "large_amethyst_bud"
    """Large Amethyst Bud (ID: 906)"""

    LARGE_FERN = "large_fern"
    """Large Fern (ID: 502)"""

    LAVA = "lava"
    """Lava (ID: 33)"""

    LAVA_CAULDRON = "lava_cauldron"
    """Lava Cauldron (ID: 333)"""

    LECTERN = "lectern"
    """Lectern (ID: 780)"""

    LEVER = "lever"
    """Lever (ID: 230)"""

    LIGHT = "light"
    """Light (ID: 465)"""

    LIGHT_BLUE_BANNER = "light_blue_banner"
    """Light Blue Banner (ID: 506)"""

    LIGHT_BLUE_BED = "light_blue_bed"
    """Light Blue Bed (ID: 106)"""

    LIGHT_BLUE_CANDLE = "light_blue_candle"
    """Light Blue Candle (ID: 873)"""

    LIGHT_BLUE_CANDLE_CAKE = "light_blue_candle_cake"
    """Cake with Light Blue Candle (ID: 890)"""

    LIGHT_BLUE_CARPET = "light_blue_carpet"
    """Light Blue Carpet (ID: 481)"""

    LIGHT_BLUE_CONCRETE = "light_blue_concrete"
    """Light Blue Concrete (ID: 649)"""

    LIGHT_BLUE_CONCRETE_POWDER = "light_blue_concrete_powder"
    """Light Blue Concrete Powder (ID: 665)"""

    LIGHT_BLUE_GLAZED_TERRACOTTA = "light_blue_glazed_terracotta"
    """Light Blue Glazed Terracotta (ID: 633)"""

    LIGHT_BLUE_SHULKER_BOX = "light_blue_shulker_box"
    """Light Blue Shulker Box (ID: 617)"""

    LIGHT_BLUE_STAINED_GLASS = "light_blue_stained_glass"
    """Light Blue Stained Glass (ID: 271)"""

    LIGHT_BLUE_STAINED_GLASS_PANE = "light_blue_stained_glass_pane"
    """Light Blue Stained Glass Pane (ID: 444)"""

    LIGHT_BLUE_TERRACOTTA = "light_blue_terracotta"
    """Light Blue Terracotta (ID: 428)"""

    LIGHT_BLUE_WALL_BANNER = "light_blue_wall_banner"
    """Light Blue Banner (ID: 522)"""

    LIGHT_BLUE_WOOL = "light_blue_wool"
    """Light Blue Wool (ID: 133)"""

    LIGHT_GRAY_BANNER = "light_gray_banner"
    """Light Gray Banner (ID: 511)"""

    LIGHT_GRAY_BED = "light_gray_bed"
    """Light Gray Bed (ID: 111)"""

    LIGHT_GRAY_CANDLE = "light_gray_candle"
    """Light Gray Candle (ID: 878)"""

    LIGHT_GRAY_CANDLE_CAKE = "light_gray_candle_cake"
    """Cake with Light Gray Candle (ID: 895)"""

    LIGHT_GRAY_CARPET = "light_gray_carpet"
    """Light Gray Carpet (ID: 486)"""

    LIGHT_GRAY_CONCRETE = "light_gray_concrete"
    """Light Gray Concrete (ID: 654)"""

    LIGHT_GRAY_CONCRETE_POWDER = "light_gray_concrete_powder"
    """Light Gray Concrete Powder (ID: 670)"""

    LIGHT_GRAY_GLAZED_TERRACOTTA = "light_gray_glazed_terracotta"
    """Light Gray Glazed Terracotta (ID: 638)"""

    LIGHT_GRAY_SHULKER_BOX = "light_gray_shulker_box"
    """Light Gray Shulker Box (ID: 622)"""

    LIGHT_GRAY_STAINED_GLASS = "light_gray_stained_glass"
    """Light Gray Stained Glass (ID: 276)"""

    LIGHT_GRAY_STAINED_GLASS_PANE = "light_gray_stained_glass_pane"
    """Light Gray Stained Glass Pane (ID: 449)"""

    LIGHT_GRAY_TERRACOTTA = "light_gray_terracotta"
    """Light Gray Terracotta (ID: 433)"""

    LIGHT_GRAY_WALL_BANNER = "light_gray_wall_banner"
    """Light Gray Banner (ID: 527)"""

    LIGHT_GRAY_WOOL = "light_gray_wool"
    """Light Gray Wool (ID: 138)"""

    LIGHT_WEIGHTED_PRESSURE_PLATE = "light_weighted_pressure_plate"
    """Light Weighted Pressure Plate (ID: 412)"""

    LIGHTNING_ROD = "lightning_rod"
    """Lightning Rod (ID: 1006)"""

    LILAC = "lilac"
    """Lilac (ID: 498)"""

    LILY_OF_THE_VALLEY = "lily_of_the_valley"
    """Lily of the Valley (ID: 160)"""

    LILY_PAD = "lily_pad"
    """Lily Pad (ID: 324)"""

    LIME_BANNER = "lime_banner"
    """Lime Banner (ID: 508)"""

    LIME_BED = "lime_bed"
    """Lime Bed (ID: 108)"""

    LIME_CANDLE = "lime_candle"
    """Lime Candle (ID: 875)"""

    LIME_CANDLE_CAKE = "lime_candle_cake"
    """Cake with Lime Candle (ID: 892)"""

    LIME_CARPET = "lime_carpet"
    """Lime Carpet (ID: 483)"""

    LIME_CONCRETE = "lime_concrete"
    """Lime Concrete (ID: 651)"""

    LIME_CONCRETE_POWDER = "lime_concrete_powder"
    """Lime Concrete Powder (ID: 667)"""

    LIME_GLAZED_TERRACOTTA = "lime_glazed_terracotta"
    """Lime Glazed Terracotta (ID: 635)"""

    LIME_SHULKER_BOX = "lime_shulker_box"
    """Lime Shulker Box (ID: 619)"""

    LIME_STAINED_GLASS = "lime_stained_glass"
    """Lime Stained Glass (ID: 273)"""

    LIME_STAINED_GLASS_PANE = "lime_stained_glass_pane"
    """Lime Stained Glass Pane (ID: 446)"""

    LIME_TERRACOTTA = "lime_terracotta"
    """Lime Terracotta (ID: 430)"""

    LIME_WALL_BANNER = "lime_wall_banner"
    """Lime Banner (ID: 524)"""

    LIME_WOOL = "lime_wool"
    """Lime Wool (ID: 135)"""

    LODESTONE = "lodestone"
    """Lodestone (ID: 848)"""

    LOOM = "loom"
    """Loom (ID: 773)"""

    MAGENTA_BANNER = "magenta_banner"
    """Magenta Banner (ID: 505)"""

    MAGENTA_BED = "magenta_bed"
    """Magenta Bed (ID: 105)"""

    MAGENTA_CANDLE = "magenta_candle"
    """Magenta Candle (ID: 872)"""

    MAGENTA_CANDLE_CAKE = "magenta_candle_cake"
    """Cake with Magenta Candle (ID: 889)"""

    MAGENTA_CARPET = "magenta_carpet"
    """Magenta Carpet (ID: 480)"""

    MAGENTA_CONCRETE = "magenta_concrete"
    """Magenta Concrete (ID: 648)"""

    MAGENTA_CONCRETE_POWDER = "magenta_concrete_powder"
    """Magenta Concrete Powder (ID: 664)"""

    MAGENTA_GLAZED_TERRACOTTA = "magenta_glazed_terracotta"
    """Magenta Glazed Terracotta (ID: 632)"""

    MAGENTA_SHULKER_BOX = "magenta_shulker_box"
    """Magenta Shulker Box (ID: 616)"""

    MAGENTA_STAINED_GLASS = "magenta_stained_glass"
    """Magenta Stained Glass (ID: 270)"""

    MAGENTA_STAINED_GLASS_PANE = "magenta_stained_glass_pane"
    """Magenta Stained Glass Pane (ID: 443)"""

    MAGENTA_TERRACOTTA = "magenta_terracotta"
    """Magenta Terracotta (ID: 427)"""

    MAGENTA_WALL_BANNER = "magenta_wall_banner"
    """Magenta Banner (ID: 521)"""

    MAGENTA_WOOL = "magenta_wool"
    """Magenta Wool (ID: 132)"""

    MAGMA_BLOCK = "magma_block"
    """Magma Block (ID: 607)"""

    MANGROVE_BUTTON = "mangrove_button"
    """Mangrove Button (ID: 392)"""

    MANGROVE_DOOR = "mangrove_door"
    """Mangrove Door (ID: 589)"""

    MANGROVE_FENCE = "mangrove_fence"
    """Mangrove Fence (ID: 581)"""

    MANGROVE_FENCE_GATE = "mangrove_fence_gate"
    """Mangrove Fence Gate (ID: 573)"""

    MANGROVE_HANGING_SIGN = "mangrove_hanging_sign"
    """Mangrove Hanging Sign (ID: 217)"""

    MANGROVE_LEAVES = "mangrove_leaves"
    """Mangrove Leaves (ID: 89)"""

    MANGROVE_LOG = "mangrove_log"
    """Mangrove Log (ID: 53)"""

    MANGROVE_PLANKS = "mangrove_planks"
    """Mangrove Planks (ID: 20)"""

    MANGROVE_PRESSURE_PLATE = "mangrove_pressure_plate"
    """Mangrove Pressure Plate (ID: 240)"""

    MANGROVE_PROPAGULE = "mangrove_propagule"
    """Mangrove Propagule (ID: 30)"""

    MANGROVE_ROOTS = "mangrove_roots"
    """Mangrove Roots (ID: 54)"""

    MANGROVE_SIGN = "mangrove_sign"
    """Mangrove Sign (ID: 193)"""

    MANGROVE_SLAB = "mangrove_slab"
    """Mangrove Slab (ID: 546)"""

    MANGROVE_STAIRS = "mangrove_stairs"
    """Mangrove Stairs (ID: 460)"""

    MANGROVE_TRAPDOOR = "mangrove_trapdoor"
    """Mangrove Trapdoor (ID: 291)"""

    MANGROVE_WALL_HANGING_SIGN = "mangrove_wall_hanging_sign"
    """Mangrove Hanging Sign (ID: 226)"""

    MANGROVE_WALL_SIGN = "mangrove_wall_sign"
    """Mangrove Sign (ID: 206)"""

    MANGROVE_WOOD = "mangrove_wood"
    """Mangrove Wood (ID: 73)"""

    MEDIUM_AMETHYST_BUD = "medium_amethyst_bud"
    """Medium Amethyst Bud (ID: 907)"""

    MELON = "melon"
    """Melon (ID: 312)"""

    MELON_STEM = "melon_stem"
    """Melon Stem (ID: 316)"""

    MOSS_BLOCK = "moss_block"
    """Moss Block (ID: 1016)"""

    MOSS_CARPET = "moss_carpet"
    """Moss Carpet (ID: 1014)"""

    MOSSY_COBBLESTONE = "mossy_cobblestone"
    """Mossy Cobblestone (ID: 169)"""

    MOSSY_COBBLESTONE_SLAB = "mossy_cobblestone_slab"
    """Mossy Cobblestone Slab (ID: 750)"""

    MOSSY_COBBLESTONE_STAIRS = "mossy_cobblestone_stairs"
    """Mossy Cobblestone Stairs (ID: 736)"""

    MOSSY_COBBLESTONE_WALL = "mossy_cobblestone_wall"
    """Mossy Cobblestone Wall (ID: 354)"""

    MOSSY_STONE_BRICK_SLAB = "mossy_stone_brick_slab"
    """Mossy Stone Brick Slab (ID: 748)"""

    MOSSY_STONE_BRICK_STAIRS = "mossy_stone_brick_stairs"
    """Mossy Stone Brick Stairs (ID: 734)"""

    MOSSY_STONE_BRICK_WALL = "mossy_stone_brick_wall"
    """Mossy Stone Brick Wall (ID: 762)"""

    MOSSY_STONE_BRICKS = "mossy_stone_bricks"
    """Mossy Stone Bricks (ID: 294)"""

    MOVING_PISTON = "moving_piston"
    """Moving Piston (ID: 146)"""

    MUD = "mud"
    """Mud (ID: 1022)"""

    MUD_BRICK_SLAB = "mud_brick_slab"
    """Mud Brick Slab (ID: 557)"""

    MUD_BRICK_STAIRS = "mud_brick_stairs"
    """Mud Brick Stairs (ID: 322)"""

    MUD_BRICK_WALL = "mud_brick_wall"
    """Mud Brick Wall (ID: 765)"""

    MUD_BRICKS = "mud_bricks"
    """Mud Bricks (ID: 298)"""

    MUDDY_MANGROVE_ROOTS = "muddy_mangrove_roots"
    """Muddy Mangrove Roots (ID: 55)"""

    MUSHROOM_STEM = "mushroom_stem"
    """Mushroom Stem (ID: 307)"""

    MYCELIUM = "mycelium"
    """Mycelium (ID: 323)"""

    NETHER_BRICK_FENCE = "nether_brick_fence"
    """Nether Brick Fence (ID: 326)"""

    NETHER_BRICK_SLAB = "nether_brick_slab"
    """Nether Brick Slab (ID: 558)"""

    NETHER_BRICK_STAIRS = "nether_brick_stairs"
    """Nether Brick Stairs (ID: 327)"""

    NETHER_BRICK_WALL = "nether_brick_wall"
    """Nether Brick Wall (ID: 766)"""

    NETHER_BRICKS = "nether_bricks"
    """Nether Bricks (ID: 325)"""

    NETHER_GOLD_ORE = "nether_gold_ore"
    """Nether Gold Ore (ID: 45)"""

    NETHER_PORTAL = "nether_portal"
    """Nether Portal (ID: 263)"""

    NETHER_QUARTZ_ORE = "nether_quartz_ore"
    """Nether Quartz Ore (ID: 417)"""

    NETHER_SPROUTS = "nether_sprouts"
    """Nether Sprouts (ID: 797)"""

    NETHER_WART = "nether_wart"
    """Nether Wart (ID: 328)"""

    NETHER_WART_BLOCK = "nether_wart_block"
    """Nether Wart Block (ID: 608)"""

    NETHERITE_BLOCK = "netherite_block"
    """Block of Netherite (ID: 840)"""

    NETHERRACK = "netherrack"
    """Netherrack (ID: 255)"""

    NOTE_BLOCK = "note_block"
    """Note Block (ID: 102)"""

    OAK_BUTTON = "oak_button"
    """Oak Button (ID: 385)"""

    OAK_DOOR = "oak_door"
    """Oak Door (ID: 195)"""

    OAK_FENCE = "oak_fence"
    """Oak Fence (ID: 254)"""

    OAK_FENCE_GATE = "oak_fence_gate"
    """Oak Fence Gate (ID: 319)"""

    OAK_HANGING_SIGN = "oak_hanging_sign"
    """Oak Hanging Sign (ID: 208)"""

    OAK_LEAVES = "oak_leaves"
    """Oak Leaves (ID: 82)"""

    OAK_LOG = "oak_log"
    """Oak Log (ID: 46)"""

    OAK_PLANKS = "oak_planks"
    """Oak Planks (ID: 13)"""

    OAK_PRESSURE_PLATE = "oak_pressure_plate"
    """Oak Pressure Plate (ID: 233)"""

    OAK_SAPLING = "oak_sapling"
    """Oak Sapling (ID: 23)"""

    OAK_SIGN = "oak_sign"
    """Oak Sign (ID: 186)"""

    OAK_SLAB = "oak_slab"
    """Oak Slab (ID: 539)"""

    OAK_STAIRS = "oak_stairs"
    """Oak Stairs (ID: 176)"""

    OAK_TRAPDOOR = "oak_trapdoor"
    """Oak Trapdoor (ID: 284)"""

    OAK_WALL_HANGING_SIGN = "oak_wall_hanging_sign"
    """Oak Hanging Sign (ID: 219)"""

    OAK_WALL_SIGN = "oak_wall_sign"
    """Oak Sign (ID: 199)"""

    OAK_WOOD = "oak_wood"
    """Oak Wood (ID: 66)"""

    OBSERVER = "observer"
    """Observer (ID: 612)"""

    OBSIDIAN = "obsidian"
    """Obsidian (ID: 170)"""

    OCHRE_FROGLIGHT = "ochre_froglight"
    """Ochre Froglight (ID: 1050)"""

    ORANGE_BANNER = "orange_banner"
    """Orange Banner (ID: 504)"""

    ORANGE_BED = "orange_bed"
    """Orange Bed (ID: 104)"""

    ORANGE_CANDLE = "orange_candle"
    """Orange Candle (ID: 871)"""

    ORANGE_CANDLE_CAKE = "orange_candle_cake"
    """Cake with Orange Candle (ID: 888)"""

    ORANGE_CARPET = "orange_carpet"
    """Orange Carpet (ID: 479)"""

    ORANGE_CONCRETE = "orange_concrete"
    """Orange Concrete (ID: 647)"""

    ORANGE_CONCRETE_POWDER = "orange_concrete_powder"
    """Orange Concrete Powder (ID: 663)"""

    ORANGE_GLAZED_TERRACOTTA = "orange_glazed_terracotta"
    """Orange Glazed Terracotta (ID: 631)"""

    ORANGE_SHULKER_BOX = "orange_shulker_box"
    """Orange Shulker Box (ID: 615)"""

    ORANGE_STAINED_GLASS = "orange_stained_glass"
    """Orange Stained Glass (ID: 269)"""

    ORANGE_STAINED_GLASS_PANE = "orange_stained_glass_pane"
    """Orange Stained Glass Pane (ID: 442)"""

    ORANGE_TERRACOTTA = "orange_terracotta"
    """Orange Terracotta (ID: 426)"""

    ORANGE_TULIP = "orange_tulip"
    """Orange Tulip (ID: 154)"""

    ORANGE_WALL_BANNER = "orange_wall_banner"
    """Orange Banner (ID: 520)"""

    ORANGE_WOOL = "orange_wool"
    """Orange Wool (ID: 131)"""

    OXEYE_DAISY = "oxeye_daisy"
    """Oxeye Daisy (ID: 157)"""

    OXIDIZED_CHISELED_COPPER = "oxidized_chiseled_copper"
    """Oxidized Chiseled Copper (ID: 942)"""

    OXIDIZED_COPPER = "oxidized_copper"
    """Oxidized Copper (ID: 935)"""

    OXIDIZED_COPPER_BULB = "oxidized_copper_bulb"
    """Oxidized Copper Bulb (ID: 1001)"""

    OXIDIZED_COPPER_DOOR = "oxidized_copper_door"
    """Oxidized Copper Door (ID: 976)"""

    OXIDIZED_COPPER_GRATE = "oxidized_copper_grate"
    """Oxidized Copper Grate (ID: 993)"""

    OXIDIZED_COPPER_TRAPDOOR = "oxidized_copper_trapdoor"
    """Oxidized Copper Trapdoor (ID: 984)"""

    OXIDIZED_CUT_COPPER = "oxidized_cut_copper"
    """Oxidized Cut Copper (ID: 938)"""

    OXIDIZED_CUT_COPPER_SLAB = "oxidized_cut_copper_slab"
    """Oxidized Cut Copper Slab (ID: 954)"""

    OXIDIZED_CUT_COPPER_STAIRS = "oxidized_cut_copper_stairs"
    """Oxidized Cut Copper Stairs (ID: 950)"""

    PACKED_ICE = "packed_ice"
    """Packed Ice (ID: 496)"""

    PACKED_MUD = "packed_mud"
    """Packed Mud (ID: 297)"""

    PEARLESCENT_FROGLIGHT = "pearlescent_froglight"
    """Pearlescent Froglight (ID: 1052)"""

    PEONY = "peony"
    """Peony (ID: 500)"""

    PETRIFIED_OAK_SLAB = "petrified_oak_slab"
    """Petrified Oak Slab (ID: 553)"""

    PIGLIN_HEAD = "piglin_head"
    """Piglin Head (ID: 406)"""

    PIGLIN_WALL_HEAD = "piglin_wall_head"
    """Piglin Head (ID: 407)"""

    PINK_BANNER = "pink_banner"
    """Pink Banner (ID: 509)"""

    PINK_BED = "pink_bed"
    """Pink Bed (ID: 109)"""

    PINK_CANDLE = "pink_candle"
    """Pink Candle (ID: 876)"""

    PINK_CANDLE_CAKE = "pink_candle_cake"
    """Cake with Pink Candle (ID: 893)"""

    PINK_CARPET = "pink_carpet"
    """Pink Carpet (ID: 484)"""

    PINK_CONCRETE = "pink_concrete"
    """Pink Concrete (ID: 652)"""

    PINK_CONCRETE_POWDER = "pink_concrete_powder"
    """Pink Concrete Powder (ID: 668)"""

    PINK_GLAZED_TERRACOTTA = "pink_glazed_terracotta"
    """Pink Glazed Terracotta (ID: 636)"""

    PINK_PETALS = "pink_petals"
    """Pink Petals (ID: 1015)"""

    PINK_SHULKER_BOX = "pink_shulker_box"
    """Pink Shulker Box (ID: 620)"""

    PINK_STAINED_GLASS = "pink_stained_glass"
    """Pink Stained Glass (ID: 274)"""

    PINK_STAINED_GLASS_PANE = "pink_stained_glass_pane"
    """Pink Stained Glass Pane (ID: 447)"""

    PINK_TERRACOTTA = "pink_terracotta"
    """Pink Terracotta (ID: 431)"""

    PINK_TULIP = "pink_tulip"
    """Pink Tulip (ID: 156)"""

    PINK_WALL_BANNER = "pink_wall_banner"
    """Pink Banner (ID: 525)"""

    PINK_WOOL = "pink_wool"
    """Pink Wool (ID: 136)"""

    PISTON = "piston"
    """Piston (ID: 128)"""

    PISTON_HEAD = "piston_head"
    """Piston Head (ID: 129)"""

    PITCHER_CROP = "pitcher_crop"
    """Pitcher Crop (ID: 599)"""

    PITCHER_PLANT = "pitcher_plant"
    """Pitcher Plant (ID: 600)"""

    PLAYER_HEAD = "player_head"
    """Player Head (ID: 400)"""

    PLAYER_WALL_HEAD = "player_wall_head"
    """Player Head (ID: 401)"""

    PODZOL = "podzol"
    """Podzol (ID: 11)"""

    POINTED_DRIPSTONE = "pointed_dripstone"
    """Pointed Dripstone (ID: 1007)"""

    POLISHED_ANDESITE = "polished_andesite"
    """Polished Andesite (ID: 7)"""

    POLISHED_ANDESITE_SLAB = "polished_andesite_slab"
    """Polished Andesite Slab (ID: 757)"""

    POLISHED_ANDESITE_STAIRS = "polished_andesite_stairs"
    """Polished Andesite Stairs (ID: 744)"""

    POLISHED_BASALT = "polished_basalt"
    """Polished Basalt (ID: 259)"""

    POLISHED_BLACKSTONE = "polished_blackstone"
    """Polished Blackstone (ID: 853)"""

    POLISHED_BLACKSTONE_BRICK_SLAB = "polished_blackstone_brick_slab"
    """Polished Blackstone Brick Slab (ID: 857)"""

    POLISHED_BLACKSTONE_BRICK_STAIRS = "polished_blackstone_brick_stairs"
    """Polished Blackstone Brick Stairs (ID: 858)"""

    POLISHED_BLACKSTONE_BRICK_WALL = "polished_blackstone_brick_wall"
    """Polished Blackstone Brick Wall (ID: 859)"""

    POLISHED_BLACKSTONE_BRICKS = "polished_blackstone_bricks"
    """Polished Blackstone Bricks (ID: 854)"""

    POLISHED_BLACKSTONE_BUTTON = "polished_blackstone_button"
    """Polished Blackstone Button (ID: 864)"""

    POLISHED_BLACKSTONE_PRESSURE_PLATE = "polished_blackstone_pressure_plate"
    """Polished Blackstone Pressure Plate (ID: 863)"""

    POLISHED_BLACKSTONE_SLAB = "polished_blackstone_slab"
    """Polished Blackstone Slab (ID: 862)"""

    POLISHED_BLACKSTONE_STAIRS = "polished_blackstone_stairs"
    """Polished Blackstone Stairs (ID: 861)"""

    POLISHED_BLACKSTONE_WALL = "polished_blackstone_wall"
    """Polished Blackstone Wall (ID: 865)"""

    POLISHED_DEEPSLATE = "polished_deepslate"
    """Polished Deepslate (ID: 1028)"""

    POLISHED_DEEPSLATE_SLAB = "polished_deepslate_slab"
    """Polished Deepslate Slab (ID: 1030)"""

    POLISHED_DEEPSLATE_STAIRS = "polished_deepslate_stairs"
    """Polished Deepslate Stairs (ID: 1029)"""

    POLISHED_DEEPSLATE_WALL = "polished_deepslate_wall"
    """Polished Deepslate Wall (ID: 1031)"""

    POLISHED_DIORITE = "polished_diorite"
    """Polished Diorite (ID: 5)"""

    POLISHED_DIORITE_SLAB = "polished_diorite_slab"
    """Polished Diorite Slab (ID: 749)"""

    POLISHED_DIORITE_STAIRS = "polished_diorite_stairs"
    """Polished Diorite Stairs (ID: 735)"""

    POLISHED_GRANITE = "polished_granite"
    """Polished Granite (ID: 3)"""

    POLISHED_GRANITE_SLAB = "polished_granite_slab"
    """Polished Granite Slab (ID: 746)"""

    POLISHED_GRANITE_STAIRS = "polished_granite_stairs"
    """Polished Granite Stairs (ID: 732)"""

    POLISHED_TUFF = "polished_tuff"
    """Polished Tuff (ID: 913)"""

    POLISHED_TUFF_SLAB = "polished_tuff_slab"
    """Polished Tuff Slab (ID: 914)"""

    POLISHED_TUFF_STAIRS = "polished_tuff_stairs"
    """Polished Tuff Stairs (ID: 915)"""

    POLISHED_TUFF_WALL = "polished_tuff_wall"
    """Polished Tuff Wall (ID: 916)"""

    POPPY = "poppy"
    """Poppy (ID: 149)"""

    POTATOES = "potatoes"
    """Potatoes (ID: 384)"""

    POTTED_ACACIA_SAPLING = "potted_acacia_sapling"
    """Potted Acacia Sapling (ID: 361)"""

    POTTED_ALLIUM = "potted_allium"
    """Potted Allium (ID: 369)"""

    POTTED_AZALEA_BUSH = "potted_azalea_bush"
    """Potted Azalea (ID: 1048)"""

    POTTED_AZURE_BLUET = "potted_azure_bluet"
    """Potted Azure Bluet (ID: 370)"""

    POTTED_BAMBOO = "potted_bamboo"
    """Potted Bamboo (ID: 728)"""

    POTTED_BIRCH_SAPLING = "potted_birch_sapling"
    """Potted Birch Sapling (ID: 359)"""

    POTTED_BLUE_ORCHID = "potted_blue_orchid"
    """Potted Blue Orchid (ID: 368)"""

    POTTED_BROWN_MUSHROOM = "potted_brown_mushroom"
    """Potted Brown Mushroom (ID: 380)"""

    POTTED_CACTUS = "potted_cactus"
    """Potted Cactus (ID: 382)"""

    POTTED_CHERRY_SAPLING = "potted_cherry_sapling"
    """Potted Cherry Sapling (ID: 362)"""

    POTTED_CORNFLOWER = "potted_cornflower"
    """Potted Cornflower (ID: 376)"""

    POTTED_CRIMSON_FUNGUS = "potted_crimson_fungus"
    """Potted Crimson Fungus (ID: 844)"""

    POTTED_CRIMSON_ROOTS = "potted_crimson_roots"
    """Potted Crimson Roots (ID: 846)"""

    POTTED_DANDELION = "potted_dandelion"
    """Potted Dandelion (ID: 366)"""

    POTTED_DARK_OAK_SAPLING = "potted_dark_oak_sapling"
    """Potted Dark Oak Sapling (ID: 363)"""

    POTTED_DEAD_BUSH = "potted_dead_bush"
    """Potted Dead Bush (ID: 381)"""

    POTTED_FERN = "potted_fern"
    """Potted Fern (ID: 365)"""

    POTTED_FLOWERING_AZALEA_BUSH = "potted_flowering_azalea_bush"
    """Potted Flowering Azalea (ID: 1049)"""

    POTTED_JUNGLE_SAPLING = "potted_jungle_sapling"
    """Potted Jungle Sapling (ID: 360)"""

    POTTED_LILY_OF_THE_VALLEY = "potted_lily_of_the_valley"
    """Potted Lily of the Valley (ID: 377)"""

    POTTED_MANGROVE_PROPAGULE = "potted_mangrove_propagule"
    """Potted Mangrove Propagule (ID: 364)"""

    POTTED_OAK_SAPLING = "potted_oak_sapling"
    """Potted Oak Sapling (ID: 357)"""

    POTTED_ORANGE_TULIP = "potted_orange_tulip"
    """Potted Orange Tulip (ID: 372)"""

    POTTED_OXEYE_DAISY = "potted_oxeye_daisy"
    """Potted Oxeye Daisy (ID: 375)"""

    POTTED_PINK_TULIP = "potted_pink_tulip"
    """Potted Pink Tulip (ID: 374)"""

    POTTED_POPPY = "potted_poppy"
    """Potted Poppy (ID: 367)"""

    POTTED_RED_MUSHROOM = "potted_red_mushroom"
    """Potted Red Mushroom (ID: 379)"""

    POTTED_RED_TULIP = "potted_red_tulip"
    """Potted Red Tulip (ID: 371)"""

    POTTED_SPRUCE_SAPLING = "potted_spruce_sapling"
    """Potted Spruce Sapling (ID: 358)"""

    POTTED_TORCHFLOWER = "potted_torchflower"
    """Potted Torchflower (ID: 356)"""

    POTTED_WARPED_FUNGUS = "potted_warped_fungus"
    """Potted Warped Fungus (ID: 845)"""

    POTTED_WARPED_ROOTS = "potted_warped_roots"
    """Potted Warped Roots (ID: 847)"""

    POTTED_WHITE_TULIP = "potted_white_tulip"
    """Potted White Tulip (ID: 373)"""

    POTTED_WITHER_ROSE = "potted_wither_rose"
    """Potted Wither Rose (ID: 378)"""

    POWDER_SNOW = "powder_snow"
    """Powder Snow (ID: 925)"""

    POWDER_SNOW_CAULDRON = "powder_snow_cauldron"
    """Powder Snow Cauldron (ID: 334)"""

    POWERED_RAIL = "powered_rail"
    """Powered Rail (ID: 119)"""

    PRISMARINE = "prismarine"
    """Prismarine (ID: 467)"""

    PRISMARINE_BRICK_SLAB = "prismarine_brick_slab"
    """Prismarine Brick Slab (ID: 474)"""

    PRISMARINE_BRICK_STAIRS = "prismarine_brick_stairs"
    """Prismarine Brick Stairs (ID: 471)"""

    PRISMARINE_BRICKS = "prismarine_bricks"
    """Prismarine Bricks (ID: 468)"""

    PRISMARINE_SLAB = "prismarine_slab"
    """Prismarine Slab (ID: 473)"""

    PRISMARINE_STAIRS = "prismarine_stairs"
    """Prismarine Stairs (ID: 470)"""

    PRISMARINE_WALL = "prismarine_wall"
    """Prismarine Wall (ID: 760)"""

    PUMPKIN = "pumpkin"
    """Pumpkin (ID: 311)"""

    PUMPKIN_STEM = "pumpkin_stem"
    """Pumpkin Stem (ID: 315)"""

    PURPLE_BANNER = "purple_banner"
    """Purple Banner (ID: 513)"""

    PURPLE_BED = "purple_bed"
    """Purple Bed (ID: 113)"""

    PURPLE_CANDLE = "purple_candle"
    """Purple Candle (ID: 880)"""

    PURPLE_CANDLE_CAKE = "purple_candle_cake"
    """Cake with Purple Candle (ID: 897)"""

    PURPLE_CARPET = "purple_carpet"
    """Purple Carpet (ID: 488)"""

    PURPLE_CONCRETE = "purple_concrete"
    """Purple Concrete (ID: 656)"""

    PURPLE_CONCRETE_POWDER = "purple_concrete_powder"
    """Purple Concrete Powder (ID: 672)"""

    PURPLE_GLAZED_TERRACOTTA = "purple_glazed_terracotta"
    """Purple Glazed Terracotta (ID: 640)"""

    PURPLE_SHULKER_BOX = "purple_shulker_box"
    """Purple Shulker Box (ID: 624)"""

    PURPLE_STAINED_GLASS = "purple_stained_glass"
    """Purple Stained Glass (ID: 278)"""

    PURPLE_STAINED_GLASS_PANE = "purple_stained_glass_pane"
    """Purple Stained Glass Pane (ID: 451)"""

    PURPLE_TERRACOTTA = "purple_terracotta"
    """Purple Terracotta (ID: 435)"""

    PURPLE_WALL_BANNER = "purple_wall_banner"
    """Purple Banner (ID: 529)"""

    PURPLE_WOOL = "purple_wool"
    """Purple Wool (ID: 140)"""

    PURPUR_BLOCK = "purpur_block"
    """Purpur Block (ID: 594)"""

    PURPUR_PILLAR = "purpur_pillar"
    """Purpur Pillar (ID: 595)"""

    PURPUR_SLAB = "purpur_slab"
    """Purpur Slab (ID: 562)"""

    PURPUR_STAIRS = "purpur_stairs"
    """Purpur Stairs (ID: 596)"""

    QUARTZ_BLOCK = "quartz_block"
    """Block of Quartz (ID: 419)"""

    QUARTZ_BRICKS = "quartz_bricks"
    """Quartz Bricks (ID: 868)"""

    QUARTZ_PILLAR = "quartz_pillar"
    """Quartz Pillar (ID: 421)"""

    QUARTZ_SLAB = "quartz_slab"
    """Quartz Slab (ID: 559)"""

    QUARTZ_STAIRS = "quartz_stairs"
    """Quartz Stairs (ID: 422)"""

    RAIL = "rail"
    """Rail (ID: 197)"""

    RAW_COPPER_BLOCK = "raw_copper_block"
    """Block of Raw Copper (ID: 1046)"""

    RAW_GOLD_BLOCK = "raw_gold_block"
    """Block of Raw Gold (ID: 1047)"""

    RAW_IRON_BLOCK = "raw_iron_block"
    """Block of Raw Iron (ID: 1045)"""

    RED_BANNER = "red_banner"
    """Red Banner (ID: 517)"""

    RED_BED = "red_bed"
    """Red Bed (ID: 117)"""

    RED_CANDLE = "red_candle"
    """Red Candle (ID: 884)"""

    RED_CANDLE_CAKE = "red_candle_cake"
    """Cake with Red Candle (ID: 901)"""

    RED_CARPET = "red_carpet"
    """Red Carpet (ID: 492)"""

    RED_CONCRETE = "red_concrete"
    """Red Concrete (ID: 660)"""

    RED_CONCRETE_POWDER = "red_concrete_powder"
    """Red Concrete Powder (ID: 676)"""

    RED_GLAZED_TERRACOTTA = "red_glazed_terracotta"
    """Red Glazed Terracotta (ID: 644)"""

    RED_MUSHROOM = "red_mushroom"
    """Red Mushroom (ID: 162)"""

    RED_MUSHROOM_BLOCK = "red_mushroom_block"
    """Red Mushroom Block (ID: 306)"""

    RED_NETHER_BRICK_SLAB = "red_nether_brick_slab"
    """Red Nether Brick Slab (ID: 756)"""

    RED_NETHER_BRICK_STAIRS = "red_nether_brick_stairs"
    """Red Nether Brick Stairs (ID: 743)"""

    RED_NETHER_BRICK_WALL = "red_nether_brick_wall"
    """Red Nether Brick Wall (ID: 768)"""

    RED_NETHER_BRICKS = "red_nether_bricks"
    """Red Nether Bricks (ID: 609)"""

    RED_SAND = "red_sand"
    """Red Sand (ID: 36)"""

    RED_SANDSTONE = "red_sandstone"
    """Red Sandstone (ID: 535)"""

    RED_SANDSTONE_SLAB = "red_sandstone_slab"
    """Red Sandstone Slab (ID: 560)"""

    RED_SANDSTONE_STAIRS = "red_sandstone_stairs"
    """Red Sandstone Stairs (ID: 538)"""

    RED_SANDSTONE_WALL = "red_sandstone_wall"
    """Red Sandstone Wall (ID: 761)"""

    RED_SHULKER_BOX = "red_shulker_box"
    """Red Shulker Box (ID: 628)"""

    RED_STAINED_GLASS = "red_stained_glass"
    """Red Stained Glass (ID: 282)"""

    RED_STAINED_GLASS_PANE = "red_stained_glass_pane"
    """Red Stained Glass Pane (ID: 455)"""

    RED_TERRACOTTA = "red_terracotta"
    """Red Terracotta (ID: 439)"""

    RED_TULIP = "red_tulip"
    """Red Tulip (ID: 153)"""

    RED_WALL_BANNER = "red_wall_banner"
    """Red Banner (ID: 533)"""

    RED_WOOL = "red_wool"
    """Red Wool (ID: 144)"""

    REDSTONE_BLOCK = "redstone_block"
    """Block of Redstone (ID: 416)"""

    REDSTONE_LAMP = "redstone_lamp"
    """Redstone Lamp (ID: 339)"""

    REDSTONE_ORE = "redstone_ore"
    """Redstone Ore (ID: 242)"""

    REDSTONE_TORCH = "redstone_torch"
    """Redstone Torch (ID: 244)"""

    REDSTONE_WALL_TORCH = "redstone_wall_torch"
    """Redstone Torch (ID: 245)"""

    REDSTONE_WIRE = "redstone_wire"
    """Redstone Wire (ID: 178)"""

    REINFORCED_DEEPSLATE = "reinforced_deepslate"
    """Reinforced Deepslate (ID: 1054)"""

    REPEATER = "repeater"
    """Redstone Repeater (ID: 267)"""

    REPEATING_COMMAND_BLOCK = "repeating_command_block"
    """Repeating Command Block (ID: 604)"""

    RESPAWN_ANCHOR = "respawn_anchor"
    """Respawn Anchor (ID: 843)"""

    ROOTED_DIRT = "rooted_dirt"
    """Rooted Dirt (ID: 1021)"""

    ROSE_BUSH = "rose_bush"
    """Rose Bush (ID: 499)"""

    SAND = "sand"
    """Sand (ID: 34)"""

    SANDSTONE = "sandstone"
    """Sandstone (ID: 99)"""

    SANDSTONE_SLAB = "sandstone_slab"
    """Sandstone Slab (ID: 551)"""

    SANDSTONE_STAIRS = "sandstone_stairs"
    """Sandstone Stairs (ID: 341)"""

    SANDSTONE_WALL = "sandstone_wall"
    """Sandstone Wall (ID: 769)"""

    SCAFFOLDING = "scaffolding"
    """Scaffolding (ID: 772)"""

    SCULK = "sculk"
    """Sculk (ID: 928)"""

    SCULK_CATALYST = "sculk_catalyst"
    """Sculk Catalyst (ID: 930)"""

    SCULK_SENSOR = "sculk_sensor"
    """Sculk Sensor (ID: 926)"""

    SCULK_SHRIEKER = "sculk_shrieker"
    """Sculk Shrieker (ID: 931)"""

    SCULK_VEIN = "sculk_vein"
    """Sculk Vein (ID: 929)"""

    SEA_LANTERN = "sea_lantern"
    """Sea Lantern (ID: 476)"""

    SEA_PICKLE = "sea_pickle"
    """Sea Pickle (ID: 723)"""

    SEAGRASS = "seagrass"
    """Seagrass (ID: 126)"""

    SHORT_GRASS = "short_grass"
    """Short Grass (ID: 123)"""

    SHROOMLIGHT = "shroomlight"
    """Shroomlight (ID: 804)"""

    SHULKER_BOX = "shulker_box"
    """Shulker Box (ID: 613)"""

    SKELETON_SKULL = "skeleton_skull"
    """Skeleton Skull (ID: 394)"""

    SKELETON_WALL_SKULL = "skeleton_wall_skull"
    """Skeleton Skull (ID: 395)"""

    SLIME_BLOCK = "slime_block"
    """Slime Block (ID: 463)"""

    SMALL_AMETHYST_BUD = "small_amethyst_bud"
    """Small Amethyst Bud (ID: 908)"""

    SMALL_DRIPLEAF = "small_dripleaf"
    """Small Dripleaf (ID: 1019)"""

    SMITHING_TABLE = "smithing_table"
    """Smithing Table (ID: 781)"""

    SMOKER = "smoker"
    """Smoker (ID: 775)"""

    SMOOTH_BASALT = "smooth_basalt"
    """Smooth Basalt (ID: 1044)"""

    SMOOTH_QUARTZ = "smooth_quartz"
    """Smooth Quartz Block (ID: 565)"""

    SMOOTH_QUARTZ_SLAB = "smooth_quartz_slab"
    """Smooth Quartz Slab (ID: 753)"""

    SMOOTH_QUARTZ_STAIRS = "smooth_quartz_stairs"
    """Smooth Quartz Stairs (ID: 740)"""

    SMOOTH_RED_SANDSTONE = "smooth_red_sandstone"
    """Smooth Red Sandstone (ID: 566)"""

    SMOOTH_RED_SANDSTONE_SLAB = "smooth_red_sandstone_slab"
    """Smooth Red Sandstone Slab (ID: 747)"""

    SMOOTH_RED_SANDSTONE_STAIRS = "smooth_red_sandstone_stairs"
    """Smooth Red Sandstone Stairs (ID: 733)"""

    SMOOTH_SANDSTONE = "smooth_sandstone"
    """Smooth Sandstone (ID: 564)"""

    SMOOTH_SANDSTONE_SLAB = "smooth_sandstone_slab"
    """Smooth Sandstone Slab (ID: 752)"""

    SMOOTH_SANDSTONE_STAIRS = "smooth_sandstone_stairs"
    """Smooth Sandstone Stairs (ID: 739)"""

    SMOOTH_STONE = "smooth_stone"
    """Smooth Stone (ID: 563)"""

    SMOOTH_STONE_SLAB = "smooth_stone_slab"
    """Smooth Stone Slab (ID: 550)"""

    SNIFFER_EGG = "sniffer_egg"
    """Sniffer Egg (ID: 682)"""

    SNOW = "snow"
    """Snow (ID: 247)"""

    SNOW_BLOCK = "snow_block"
    """Snow Block (ID: 249)"""

    SOUL_CAMPFIRE = "soul_campfire"
    """Soul Campfire (ID: 787)"""

    SOUL_FIRE = "soul_fire"
    """Soul Fire (ID: 174)"""

    SOUL_LANTERN = "soul_lantern"
    """Soul Lantern (ID: 785)"""

    SOUL_SAND = "soul_sand"
    """Soul Sand (ID: 256)"""

    SOUL_SOIL = "soul_soil"
    """Soul Soil (ID: 257)"""

    SOUL_TORCH = "soul_torch"
    """Soul Torch (ID: 260)"""

    SOUL_WALL_TORCH = "soul_wall_torch"
    """Soul Torch (ID: 261)"""

    SPAWNER = "spawner"
    """Monster Spawner (ID: 175)"""

    SPONGE = "sponge"
    """Sponge (ID: 92)"""

    SPORE_BLOSSOM = "spore_blossom"
    """Spore Blossom (ID: 1011)"""

    SPRUCE_BUTTON = "spruce_button"
    """Spruce Button (ID: 386)"""

    SPRUCE_DOOR = "spruce_door"
    """Spruce Door (ID: 583)"""

    SPRUCE_FENCE = "spruce_fence"
    """Spruce Fence (ID: 575)"""

    SPRUCE_FENCE_GATE = "spruce_fence_gate"
    """Spruce Fence Gate (ID: 567)"""

    SPRUCE_HANGING_SIGN = "spruce_hanging_sign"
    """Spruce Hanging Sign (ID: 209)"""

    SPRUCE_LEAVES = "spruce_leaves"
    """Spruce Leaves (ID: 83)"""

    SPRUCE_LOG = "spruce_log"
    """Spruce Log (ID: 47)"""

    SPRUCE_PLANKS = "spruce_planks"
    """Spruce Planks (ID: 14)"""

    SPRUCE_PRESSURE_PLATE = "spruce_pressure_plate"
    """Spruce Pressure Plate (ID: 234)"""

    SPRUCE_SAPLING = "spruce_sapling"
    """Spruce Sapling (ID: 24)"""

    SPRUCE_SIGN = "spruce_sign"
    """Spruce Sign (ID: 187)"""

    SPRUCE_SLAB = "spruce_slab"
    """Spruce Slab (ID: 540)"""

    SPRUCE_STAIRS = "spruce_stairs"
    """Spruce Stairs (ID: 348)"""

    SPRUCE_TRAPDOOR = "spruce_trapdoor"
    """Spruce Trapdoor (ID: 285)"""

    SPRUCE_WALL_HANGING_SIGN = "spruce_wall_hanging_sign"
    """Spruce Hanging Sign (ID: 220)"""

    SPRUCE_WALL_SIGN = "spruce_wall_sign"
    """Spruce Sign (ID: 200)"""

    SPRUCE_WOOD = "spruce_wood"
    """Spruce Wood (ID: 67)"""

    STICKY_PISTON = "sticky_piston"
    """Sticky Piston (ID: 121)"""

    STONE = "stone"
    """Stone (ID: 1)"""

    STONE_BRICK_SLAB = "stone_brick_slab"
    """Stone Brick Slab (ID: 556)"""

    STONE_BRICK_STAIRS = "stone_brick_stairs"
    """Stone Brick Stairs (ID: 321)"""

    STONE_BRICK_WALL = "stone_brick_wall"
    """Stone Brick Wall (ID: 764)"""

    STONE_BRICKS = "stone_bricks"
    """Stone Bricks (ID: 293)"""

    STONE_BUTTON = "stone_button"
    """Stone Button (ID: 246)"""

    STONE_PRESSURE_PLATE = "stone_pressure_plate"
    """Stone Pressure Plate (ID: 231)"""

    STONE_SLAB = "stone_slab"
    """Stone Slab (ID: 549)"""

    STONE_STAIRS = "stone_stairs"
    """Stone Stairs (ID: 738)"""

    STONECUTTER = "stonecutter"
    """Stonecutter (ID: 782)"""

    STRIPPED_ACACIA_LOG = "stripped_acacia_log"
    """Stripped Acacia Log (ID: 60)"""

    STRIPPED_ACACIA_WOOD = "stripped_acacia_wood"
    """Stripped Acacia Wood (ID: 78)"""

    STRIPPED_BAMBOO_BLOCK = "stripped_bamboo_block"
    """Block of Stripped Bamboo (ID: 65)"""

    STRIPPED_BIRCH_LOG = "stripped_birch_log"
    """Stripped Birch Log (ID: 58)"""

    STRIPPED_BIRCH_WOOD = "stripped_birch_wood"
    """Stripped Birch Wood (ID: 76)"""

    STRIPPED_CHERRY_LOG = "stripped_cherry_log"
    """Stripped Cherry Log (ID: 61)"""

    STRIPPED_CHERRY_WOOD = "stripped_cherry_wood"
    """Stripped Cherry Wood (ID: 79)"""

    STRIPPED_CRIMSON_HYPHAE = "stripped_crimson_hyphae"
    """Stripped Crimson Hyphae (ID: 801)"""

    STRIPPED_CRIMSON_STEM = "stripped_crimson_stem"
    """Stripped Crimson Stem (ID: 799)"""

    STRIPPED_DARK_OAK_LOG = "stripped_dark_oak_log"
    """Stripped Dark Oak Log (ID: 62)"""

    STRIPPED_DARK_OAK_WOOD = "stripped_dark_oak_wood"
    """Stripped Dark Oak Wood (ID: 80)"""

    STRIPPED_JUNGLE_LOG = "stripped_jungle_log"
    """Stripped Jungle Log (ID: 59)"""

    STRIPPED_JUNGLE_WOOD = "stripped_jungle_wood"
    """Stripped Jungle Wood (ID: 77)"""

    STRIPPED_MANGROVE_LOG = "stripped_mangrove_log"
    """Stripped Mangrove Log (ID: 64)"""

    STRIPPED_MANGROVE_WOOD = "stripped_mangrove_wood"
    """Stripped Mangrove Wood (ID: 81)"""

    STRIPPED_OAK_LOG = "stripped_oak_log"
    """Stripped Oak Log (ID: 63)"""

    STRIPPED_OAK_WOOD = "stripped_oak_wood"
    """Stripped Oak Wood (ID: 74)"""

    STRIPPED_SPRUCE_LOG = "stripped_spruce_log"
    """Stripped Spruce Log (ID: 57)"""

    STRIPPED_SPRUCE_WOOD = "stripped_spruce_wood"
    """Stripped Spruce Wood (ID: 75)"""

    STRIPPED_WARPED_HYPHAE = "stripped_warped_hyphae"
    """Stripped Warped Hyphae (ID: 792)"""

    STRIPPED_WARPED_STEM = "stripped_warped_stem"
    """Stripped Warped Stem (ID: 790)"""

    STRUCTURE_BLOCK = "structure_block"
    """Structure Block (ID: 832)"""

    STRUCTURE_VOID = "structure_void"
    """Structure Void (ID: 611)"""

    SUGAR_CANE = "sugar_cane"
    """Sugar Cane (ID: 252)"""

    SUNFLOWER = "sunflower"
    """Sunflower (ID: 497)"""

    SUSPICIOUS_GRAVEL = "suspicious_gravel"
    """Suspicious Gravel (ID: 38)"""

    SUSPICIOUS_SAND = "suspicious_sand"
    """Suspicious Sand (ID: 35)"""

    SWEET_BERRY_BUSH = "sweet_berry_bush"
    """Sweet Berry Bush (ID: 788)"""

    TALL_GRASS = "tall_grass"
    """Tall Grass (ID: 501)"""

    TALL_SEAGRASS = "tall_seagrass"
    """Tall Seagrass (ID: 127)"""

    TARGET = "target"
    """Target (ID: 835)"""

    TERRACOTTA = "terracotta"
    """Terracotta (ID: 494)"""

    TINTED_GLASS = "tinted_glass"
    """Tinted Glass (ID: 924)"""

    TNT = "tnt"
    """TNT (ID: 166)"""

    TORCH = "torch"
    """Torch (ID: 171)"""

    TORCHFLOWER = "torchflower"
    """Torchflower (ID: 148)"""

    TORCHFLOWER_CROP = "torchflower_crop"
    """Torchflower Crop (ID: 598)"""

    TRAPPED_CHEST = "trapped_chest"
    """Trapped Chest (ID: 411)"""

    TRIAL_SPAWNER = "trial_spawner"
    """Trial Spawner (ID: 1057)"""

    TRIPWIRE = "tripwire"
    """Tripwire (ID: 346)"""

    TRIPWIRE_HOOK = "tripwire_hook"
    """Tripwire Hook (ID: 345)"""

    TUBE_CORAL = "tube_coral"
    """Tube Coral (ID: 698)"""

    TUBE_CORAL_BLOCK = "tube_coral_block"
    """Tube Coral Block (ID: 688)"""

    TUBE_CORAL_FAN = "tube_coral_fan"
    """Tube Coral Fan (ID: 708)"""

    TUBE_CORAL_WALL_FAN = "tube_coral_wall_fan"
    """Tube Coral Wall Fan (ID: 718)"""

    TUFF = "tuff"
    """Tuff (ID: 909)"""

    TUFF_BRICK_SLAB = "tuff_brick_slab"
    """Tuff Brick Slab (ID: 919)"""

    TUFF_BRICK_STAIRS = "tuff_brick_stairs"
    """Tuff Brick Stairs (ID: 920)"""

    TUFF_BRICK_WALL = "tuff_brick_wall"
    """Tuff Brick Wall (ID: 921)"""

    TUFF_BRICKS = "tuff_bricks"
    """Tuff Bricks (ID: 918)"""

    TUFF_SLAB = "tuff_slab"
    """Tuff Slab (ID: 910)"""

    TUFF_STAIRS = "tuff_stairs"
    """Tuff Stairs (ID: 911)"""

    TUFF_WALL = "tuff_wall"
    """Tuff Wall (ID: 912)"""

    TURTLE_EGG = "turtle_egg"
    """Turtle Egg (ID: 681)"""

    TWISTING_VINES = "twisting_vines"
    """Twisting Vines (ID: 807)"""

    TWISTING_VINES_PLANT = "twisting_vines_plant"
    """Twisting Vines Plant (ID: 808)"""

    VERDANT_FROGLIGHT = "verdant_froglight"
    """Verdant Froglight (ID: 1051)"""

    VINE = "vine"
    """Vines (ID: 317)"""

    VOID_AIR = "void_air"
    """Void Air (ID: 729)"""

    WALL_TORCH = "wall_torch"
    """Torch (ID: 172)"""

    WARPED_BUTTON = "warped_button"
    """Warped Button (ID: 825)"""

    WARPED_DOOR = "warped_door"
    """Warped Door (ID: 827)"""

    WARPED_FENCE = "warped_fence"
    """Warped Fence (ID: 817)"""

    WARPED_FENCE_GATE = "warped_fence_gate"
    """Warped Fence Gate (ID: 821)"""

    WARPED_FUNGUS = "warped_fungus"
    """Warped Fungus (ID: 794)"""

    WARPED_HANGING_SIGN = "warped_hanging_sign"
    """Warped Hanging Sign (ID: 216)"""

    WARPED_HYPHAE = "warped_hyphae"
    """Warped Hyphae (ID: 791)"""

    WARPED_NYLIUM = "warped_nylium"
    """Warped Nylium (ID: 793)"""

    WARPED_PLANKS = "warped_planks"
    """Warped Planks (ID: 811)"""

    WARPED_PRESSURE_PLATE = "warped_pressure_plate"
    """Warped Pressure Plate (ID: 815)"""

    WARPED_ROOTS = "warped_roots"
    """Warped Roots (ID: 796)"""

    WARPED_SIGN = "warped_sign"
    """Warped Sign (ID: 829)"""

    WARPED_SLAB = "warped_slab"
    """Warped Slab (ID: 813)"""

    WARPED_STAIRS = "warped_stairs"
    """Warped Stairs (ID: 823)"""

    WARPED_STEM = "warped_stem"
    """Warped Stem (ID: 789)"""

    WARPED_TRAPDOOR = "warped_trapdoor"
    """Warped Trapdoor (ID: 819)"""

    WARPED_WALL_HANGING_SIGN = "warped_wall_hanging_sign"
    """Warped Hanging Sign (ID: 228)"""

    WARPED_WALL_SIGN = "warped_wall_sign"
    """Warped Sign (ID: 831)"""

    WARPED_WART_BLOCK = "warped_wart_block"
    """Warped Wart Block (ID: 795)"""

    WATER = "water"
    """Water (ID: 32)"""

    WATER_CAULDRON = "water_cauldron"
    """Water Cauldron (ID: 332)"""

    WAXED_CHISELED_COPPER = "waxed_chiseled_copper"
    """Waxed Chiseled Copper (ID: 949)"""

    WAXED_COPPER_BLOCK = "waxed_copper_block"
    """Waxed Block of Copper (ID: 958)"""

    WAXED_COPPER_BULB = "waxed_copper_bulb"
    """Waxed Copper Bulb (ID: 1002)"""

    WAXED_COPPER_DOOR = "waxed_copper_door"
    """Waxed Copper Door (ID: 978)"""

    WAXED_COPPER_GRATE = "waxed_copper_grate"
    """Waxed Copper Grate (ID: 994)"""

    WAXED_COPPER_TRAPDOOR = "waxed_copper_trapdoor"
    """Waxed Copper Trapdoor (ID: 986)"""

    WAXED_CUT_COPPER = "waxed_cut_copper"
    """Waxed Cut Copper (ID: 965)"""

    WAXED_CUT_COPPER_SLAB = "waxed_cut_copper_slab"
    """Waxed Cut Copper Slab (ID: 973)"""

    WAXED_CUT_COPPER_STAIRS = "waxed_cut_copper_stairs"
    """Waxed Cut Copper Stairs (ID: 969)"""

    WAXED_EXPOSED_CHISELED_COPPER = "waxed_exposed_chiseled_copper"
    """Waxed Exposed Chiseled Copper (ID: 948)"""

    WAXED_EXPOSED_COPPER = "waxed_exposed_copper"
    """Waxed Exposed Copper (ID: 960)"""

    WAXED_EXPOSED_COPPER_BULB = "waxed_exposed_copper_bulb"
    """Waxed Exposed Copper Bulb (ID: 1003)"""

    WAXED_EXPOSED_COPPER_DOOR = "waxed_exposed_copper_door"
    """Waxed Exposed Copper Door (ID: 979)"""

    WAXED_EXPOSED_COPPER_GRATE = "waxed_exposed_copper_grate"
    """Waxed Exposed Copper Grate (ID: 995)"""

    WAXED_EXPOSED_COPPER_TRAPDOOR = "waxed_exposed_copper_trapdoor"
    """Waxed Exposed Copper Trapdoor (ID: 987)"""

    WAXED_EXPOSED_CUT_COPPER = "waxed_exposed_cut_copper"
    """Waxed Exposed Cut Copper (ID: 964)"""

    WAXED_EXPOSED_CUT_COPPER_SLAB = "waxed_exposed_cut_copper_slab"
    """Waxed Exposed Cut Copper Slab (ID: 972)"""

    WAXED_EXPOSED_CUT_COPPER_STAIRS = "waxed_exposed_cut_copper_stairs"
    """Waxed Exposed Cut Copper Stairs (ID: 968)"""

    WAXED_OXIDIZED_CHISELED_COPPER = "waxed_oxidized_chiseled_copper"
    """Waxed Oxidized Chiseled Copper (ID: 946)"""

    WAXED_OXIDIZED_COPPER = "waxed_oxidized_copper"
    """Waxed Oxidized Copper (ID: 961)"""

    WAXED_OXIDIZED_COPPER_BULB = "waxed_oxidized_copper_bulb"
    """Waxed Oxidized Copper Bulb (ID: 1005)"""

    WAXED_OXIDIZED_COPPER_DOOR = "waxed_oxidized_copper_door"
    """Waxed Oxidized Copper Door (ID: 980)"""

    WAXED_OXIDIZED_COPPER_GRATE = "waxed_oxidized_copper_grate"
    """Waxed Oxidized Copper Grate (ID: 997)"""

    WAXED_OXIDIZED_COPPER_TRAPDOOR = "waxed_oxidized_copper_trapdoor"
    """Waxed Oxidized Copper Trapdoor (ID: 988)"""

    WAXED_OXIDIZED_CUT_COPPER = "waxed_oxidized_cut_copper"
    """Waxed Oxidized Cut Copper (ID: 962)"""

    WAXED_OXIDIZED_CUT_COPPER_SLAB = "waxed_oxidized_cut_copper_slab"
    """Waxed Oxidized Cut Copper Slab (ID: 970)"""

    WAXED_OXIDIZED_CUT_COPPER_STAIRS = "waxed_oxidized_cut_copper_stairs"
    """Waxed Oxidized Cut Copper Stairs (ID: 966)"""

    WAXED_WEATHERED_CHISELED_COPPER = "waxed_weathered_chiseled_copper"
    """Waxed Weathered Chiseled Copper (ID: 947)"""

    WAXED_WEATHERED_COPPER = "waxed_weathered_copper"
    """Waxed Weathered Copper (ID: 959)"""

    WAXED_WEATHERED_COPPER_BULB = "waxed_weathered_copper_bulb"
    """Waxed Weathered Copper Bulb (ID: 1004)"""

    WAXED_WEATHERED_COPPER_DOOR = "waxed_weathered_copper_door"
    """Waxed Weathered Copper Door (ID: 981)"""

    WAXED_WEATHERED_COPPER_GRATE = "waxed_weathered_copper_grate"
    """Waxed Weathered Copper Grate (ID: 996)"""

    WAXED_WEATHERED_COPPER_TRAPDOOR = "waxed_weathered_copper_trapdoor"
    """Waxed Weathered Copper Trapdoor (ID: 989)"""

    WAXED_WEATHERED_CUT_COPPER = "waxed_weathered_cut_copper"
    """Waxed Weathered Cut Copper (ID: 963)"""

    WAXED_WEATHERED_CUT_COPPER_SLAB = "waxed_weathered_cut_copper_slab"
    """Waxed Weathered Cut Copper Slab (ID: 971)"""

    WAXED_WEATHERED_CUT_COPPER_STAIRS = "waxed_weathered_cut_copper_stairs"
    """Waxed Weathered Cut Copper Stairs (ID: 967)"""

    WEATHERED_CHISELED_COPPER = "weathered_chiseled_copper"
    """Weathered Chiseled Copper (ID: 943)"""

    WEATHERED_COPPER = "weathered_copper"
    """Weathered Copper (ID: 934)"""

    WEATHERED_COPPER_BULB = "weathered_copper_bulb"
    """Weathered Copper Bulb (ID: 1000)"""

    WEATHERED_COPPER_DOOR = "weathered_copper_door"
    """Weathered Copper Door (ID: 977)"""

    WEATHERED_COPPER_GRATE = "weathered_copper_grate"
    """Weathered Copper Grate (ID: 992)"""

    WEATHERED_COPPER_TRAPDOOR = "weathered_copper_trapdoor"
    """Weathered Copper Trapdoor (ID: 985)"""

    WEATHERED_CUT_COPPER = "weathered_cut_copper"
    """Weathered Cut Copper (ID: 939)"""

    WEATHERED_CUT_COPPER_SLAB = "weathered_cut_copper_slab"
    """Weathered Cut Copper Slab (ID: 955)"""

    WEATHERED_CUT_COPPER_STAIRS = "weathered_cut_copper_stairs"
    """Weathered Cut Copper Stairs (ID: 951)"""

    WEEPING_VINES = "weeping_vines"
    """Weeping Vines (ID: 805)"""

    WEEPING_VINES_PLANT = "weeping_vines_plant"
    """Weeping Vines Plant (ID: 806)"""

    WET_SPONGE = "wet_sponge"
    """Wet Sponge (ID: 93)"""

    WHEAT = "wheat"
    """Wheat Crops (ID: 183)"""

    WHITE_BANNER = "white_banner"
    """White Banner (ID: 503)"""

    WHITE_BED = "white_bed"
    """White Bed (ID: 103)"""

    WHITE_CANDLE = "white_candle"
    """White Candle (ID: 870)"""

    WHITE_CANDLE_CAKE = "white_candle_cake"
    """Cake with White Candle (ID: 887)"""

    WHITE_CARPET = "white_carpet"
    """White Carpet (ID: 478)"""

    WHITE_CONCRETE = "white_concrete"
    """White Concrete (ID: 646)"""

    WHITE_CONCRETE_POWDER = "white_concrete_powder"
    """White Concrete Powder (ID: 662)"""

    WHITE_GLAZED_TERRACOTTA = "white_glazed_terracotta"
    """White Glazed Terracotta (ID: 630)"""

    WHITE_SHULKER_BOX = "white_shulker_box"
    """White Shulker Box (ID: 614)"""

    WHITE_STAINED_GLASS = "white_stained_glass"
    """White Stained Glass (ID: 268)"""

    WHITE_STAINED_GLASS_PANE = "white_stained_glass_pane"
    """White Stained Glass Pane (ID: 441)"""

    WHITE_TERRACOTTA = "white_terracotta"
    """White Terracotta (ID: 425)"""

    WHITE_TULIP = "white_tulip"
    """White Tulip (ID: 155)"""

    WHITE_WALL_BANNER = "white_wall_banner"
    """White Banner (ID: 519)"""

    WHITE_WOOL = "white_wool"
    """White Wool (ID: 130)"""

    WITHER_ROSE = "wither_rose"
    """Wither Rose (ID: 159)"""

    WITHER_SKELETON_SKULL = "wither_skeleton_skull"
    """Wither Skeleton Skull (ID: 396)"""

    WITHER_SKELETON_WALL_SKULL = "wither_skeleton_wall_skull"
    """Wither Skeleton Skull (ID: 397)"""

    YELLOW_BANNER = "yellow_banner"
    """Yellow Banner (ID: 507)"""

    YELLOW_BED = "yellow_bed"
    """Yellow Bed (ID: 107)"""

    YELLOW_CANDLE = "yellow_candle"
    """Yellow Candle (ID: 874)"""

    YELLOW_CANDLE_CAKE = "yellow_candle_cake"
    """Cake with Yellow Candle (ID: 891)"""

    YELLOW_CARPET = "yellow_carpet"
    """Yellow Carpet (ID: 482)"""

    YELLOW_CONCRETE = "yellow_concrete"
    """Yellow Concrete (ID: 650)"""

    YELLOW_CONCRETE_POWDER = "yellow_concrete_powder"
    """Yellow Concrete Powder (ID: 666)"""

    YELLOW_GLAZED_TERRACOTTA = "yellow_glazed_terracotta"
    """Yellow Glazed Terracotta (ID: 634)"""

    YELLOW_SHULKER_BOX = "yellow_shulker_box"
    """Yellow Shulker Box (ID: 618)"""

    YELLOW_STAINED_GLASS = "yellow_stained_glass"
    """Yellow Stained Glass (ID: 272)"""

    YELLOW_STAINED_GLASS_PANE = "yellow_stained_glass_pane"
    """Yellow Stained Glass Pane (ID: 445)"""

    YELLOW_TERRACOTTA = "yellow_terracotta"
    """Yellow Terracotta (ID: 429)"""

    YELLOW_WALL_BANNER = "yellow_wall_banner"
    """Yellow Banner (ID: 523)"""

    YELLOW_WOOL = "yellow_wool"
    """Yellow Wool (ID: 134)"""

    ZOMBIE_HEAD = "zombie_head"
    """Zombie Head (ID: 398)"""

    ZOMBIE_WALL_HEAD = "zombie_wall_head"
    """Zombie Head (ID: 399)"""


class MCItems(MCEnum):
    """Item types representing all obtainable items in Minecraft.

    All values are sourced from minecraft-data and match the game's internal identifiers.
    """

    ACACIA_BOAT = "acacia_boat"
    """Acacia Boat (ID: 781)"""

    ACACIA_BUTTON = "acacia_button"
    """Acacia Button (ID: 687)"""

    ACACIA_CHEST_BOAT = "acacia_chest_boat"
    """Acacia Boat with Chest (ID: 782)"""

    ACACIA_DOOR = "acacia_door"
    """Acacia Door (ID: 714)"""

    ACACIA_FENCE = "acacia_fence"
    """Acacia Fence (ID: 314)"""

    ACACIA_FENCE_GATE = "acacia_fence_gate"
    """Acacia Fence Gate (ID: 753)"""

    ACACIA_HANGING_SIGN = "acacia_hanging_sign"
    """Acacia Hanging Sign (ID: 898)"""

    ACACIA_LEAVES = "acacia_leaves"
    """Acacia Leaves (ID: 179)"""

    ACACIA_LOG = "acacia_log"
    """Acacia Log (ID: 135)"""

    ACACIA_PLANKS = "acacia_planks"
    """Acacia Planks (ID: 40)"""

    ACACIA_PRESSURE_PLATE = "acacia_pressure_plate"
    """Acacia Pressure Plate (ID: 702)"""

    ACACIA_SAPLING = "acacia_sapling"
    """Acacia Sapling (ID: 52)"""

    ACACIA_SIGN = "acacia_sign"
    """Acacia Sign (ID: 887)"""

    ACACIA_SLAB = "acacia_slab"
    """Acacia Slab (ID: 255)"""

    ACACIA_STAIRS = "acacia_stairs"
    """Acacia Stairs (ID: 386)"""

    ACACIA_TRAPDOOR = "acacia_trapdoor"
    """Acacia Trapdoor (ID: 734)"""

    ACACIA_WOOD = "acacia_wood"
    """Acacia Wood (ID: 169)"""

    ACTIVATOR_RAIL = "activator_rail"
    """Activator Rail (ID: 763)"""

    AIR = "air"
    """Air (ID: 0)"""

    ALLAY_SPAWN_EGG = "allay_spawn_egg"
    """Allay Spawn Egg (ID: 1005)"""

    ALLIUM = "allium"
    """Allium (ID: 220)"""

    AMETHYST_BLOCK = "amethyst_block"
    """Block of Amethyst (ID: 85)"""

    AMETHYST_CLUSTER = "amethyst_cluster"
    """Amethyst Cluster (ID: 1249)"""

    AMETHYST_SHARD = "amethyst_shard"
    """Amethyst Shard (ID: 805)"""

    ANCIENT_DEBRIS = "ancient_debris"
    """Ancient Debris (ID: 80)"""

    ANDESITE = "andesite"
    """Andesite (ID: 6)"""

    ANDESITE_SLAB = "andesite_slab"
    """Andesite Slab (ID: 647)"""

    ANDESITE_STAIRS = "andesite_stairs"
    """Andesite Stairs (ID: 630)"""

    ANDESITE_WALL = "andesite_wall"
    """Andesite Wall (ID: 406)"""

    ANGLER_POTTERY_SHERD = "angler_pottery_sherd"
    """Angler Pottery Sherd (ID: 1274)"""

    ANVIL = "anvil"
    """Anvil (ID: 418)"""

    APPLE = "apple"
    """Apple (ID: 796)"""

    ARCHER_POTTERY_SHERD = "archer_pottery_sherd"
    """Archer Pottery Sherd (ID: 1275)"""

    ARMOR_STAND = "armor_stand"
    """Armor Stand (ID: 1116)"""

    ARMS_UP_POTTERY_SHERD = "arms_up_pottery_sherd"
    """Arms Up Pottery Sherd (ID: 1276)"""

    ARROW = "arrow"
    """Arrow (ID: 798)"""

    AXOLOTL_BUCKET = "axolotl_bucket"
    """Bucket of Axolotl (ID: 916)"""

    AXOLOTL_SPAWN_EGG = "axolotl_spawn_egg"
    """Axolotl Spawn Egg (ID: 1006)"""

    AZALEA = "azalea"
    """Azalea (ID: 196)"""

    AZALEA_LEAVES = "azalea_leaves"
    """Azalea Leaves (ID: 183)"""

    AZURE_BLUET = "azure_bluet"
    """Azure Bluet (ID: 221)"""

    BAKED_POTATO = "baked_potato"
    """Baked Potato (ID: 1092)"""

    BAMBOO = "bamboo"
    """Bamboo (ID: 250)"""

    BAMBOO_BLOCK = "bamboo_block"
    """Block of Bamboo (ID: 143)"""

    BAMBOO_BUTTON = "bamboo_button"
    """Bamboo Button (ID: 691)"""

    BAMBOO_CHEST_RAFT = "bamboo_chest_raft"
    """Bamboo Raft with Chest (ID: 790)"""

    BAMBOO_DOOR = "bamboo_door"
    """Bamboo Door (ID: 718)"""

    BAMBOO_FENCE = "bamboo_fence"
    """Bamboo Fence (ID: 318)"""

    BAMBOO_FENCE_GATE = "bamboo_fence_gate"
    """Bamboo Fence Gate (ID: 757)"""

    BAMBOO_HANGING_SIGN = "bamboo_hanging_sign"
    """Bamboo Hanging Sign (ID: 902)"""

    BAMBOO_MOSAIC = "bamboo_mosaic"
    """Bamboo Mosaic (ID: 47)"""

    BAMBOO_MOSAIC_SLAB = "bamboo_mosaic_slab"
    """Bamboo Mosaic Slab (ID: 260)"""

    BAMBOO_MOSAIC_STAIRS = "bamboo_mosaic_stairs"
    """Bamboo Mosaic Stairs (ID: 391)"""

    BAMBOO_PLANKS = "bamboo_planks"
    """Bamboo Planks (ID: 44)"""

    BAMBOO_PRESSURE_PLATE = "bamboo_pressure_plate"
    """Bamboo Pressure Plate (ID: 706)"""

    BAMBOO_RAFT = "bamboo_raft"
    """Bamboo Raft (ID: 789)"""

    BAMBOO_SIGN = "bamboo_sign"
    """Bamboo Sign (ID: 891)"""

    BAMBOO_SLAB = "bamboo_slab"
    """Bamboo Slab (ID: 259)"""

    BAMBOO_STAIRS = "bamboo_stairs"
    """Bamboo Stairs (ID: 390)"""

    BAMBOO_TRAPDOOR = "bamboo_trapdoor"
    """Bamboo Trapdoor (ID: 738)"""

    BARREL = "barrel"
    """Barrel (ID: 1193)"""

    BARRIER = "barrier"
    """Barrier (ID: 442)"""

    BASALT = "basalt"
    """Basalt (ID: 327)"""

    BAT_SPAWN_EGG = "bat_spawn_egg"
    """Bat Spawn Egg (ID: 1007)"""

    BEACON = "beacon"
    """Beacon (ID: 395)"""

    BEDROCK = "bedrock"
    """Bedrock (ID: 56)"""

    BEE_NEST = "bee_nest"
    """Bee Nest (ID: 1210)"""

    BEE_SPAWN_EGG = "bee_spawn_egg"
    """Bee Spawn Egg (ID: 1008)"""

    BEEF = "beef"
    """Raw Beef (ID: 985)"""

    BEEHIVE = "beehive"
    """Beehive (ID: 1211)"""

    BEETROOT = "beetroot"
    """Beetroot (ID: 1147)"""

    BEETROOT_SEEDS = "beetroot_seeds"
    """Beetroot Seeds (ID: 1148)"""

    BEETROOT_SOUP = "beetroot_soup"
    """Beetroot Soup (ID: 1149)"""

    BELL = "bell"
    """Bell (ID: 1201)"""

    BIG_DRIPLEAF = "big_dripleaf"
    """Big Dripleaf (ID: 248)"""

    BIRCH_BOAT = "birch_boat"
    """Birch Boat (ID: 777)"""

    BIRCH_BUTTON = "birch_button"
    """Birch Button (ID: 685)"""

    BIRCH_CHEST_BOAT = "birch_chest_boat"
    """Birch Boat with Chest (ID: 778)"""

    BIRCH_DOOR = "birch_door"
    """Birch Door (ID: 712)"""

    BIRCH_FENCE = "birch_fence"
    """Birch Fence (ID: 312)"""

    BIRCH_FENCE_GATE = "birch_fence_gate"
    """Birch Fence Gate (ID: 751)"""

    BIRCH_HANGING_SIGN = "birch_hanging_sign"
    """Birch Hanging Sign (ID: 896)"""

    BIRCH_LEAVES = "birch_leaves"
    """Birch Leaves (ID: 177)"""

    BIRCH_LOG = "birch_log"
    """Birch Log (ID: 133)"""

    BIRCH_PLANKS = "birch_planks"
    """Birch Planks (ID: 38)"""

    BIRCH_PRESSURE_PLATE = "birch_pressure_plate"
    """Birch Pressure Plate (ID: 700)"""

    BIRCH_SAPLING = "birch_sapling"
    """Birch Sapling (ID: 50)"""

    BIRCH_SIGN = "birch_sign"
    """Birch Sign (ID: 885)"""

    BIRCH_SLAB = "birch_slab"
    """Birch Slab (ID: 253)"""

    BIRCH_STAIRS = "birch_stairs"
    """Birch Stairs (ID: 384)"""

    BIRCH_TRAPDOOR = "birch_trapdoor"
    """Birch Trapdoor (ID: 732)"""

    BIRCH_WOOD = "birch_wood"
    """Birch Wood (ID: 167)"""

    BLACK_BANNER = "black_banner"
    """Black Banner (ID: 1141)"""

    BLACK_BED = "black_bed"
    """Black Bed (ID: 976)"""

    BLACK_CANDLE = "black_candle"
    """Black Candle (ID: 1245)"""

    BLACK_CARPET = "black_carpet"
    """Black Carpet (ID: 460)"""

    BLACK_CONCRETE = "black_concrete"
    """Black Concrete (ID: 569)"""

    BLACK_CONCRETE_POWDER = "black_concrete_powder"
    """Black Concrete Powder (ID: 585)"""

    BLACK_DYE = "black_dye"
    """Black Dye (ID: 956)"""

    BLACK_GLAZED_TERRACOTTA = "black_glazed_terracotta"
    """Black Glazed Terracotta (ID: 553)"""

    BLACK_SHULKER_BOX = "black_shulker_box"
    """Black Shulker Box (ID: 537)"""

    BLACK_STAINED_GLASS = "black_stained_glass"
    """Black Stained Glass (ID: 485)"""

    BLACK_STAINED_GLASS_PANE = "black_stained_glass_pane"
    """Black Stained Glass Pane (ID: 501)"""

    BLACK_TERRACOTTA = "black_terracotta"
    """Black Terracotta (ID: 441)"""

    BLACK_WOOL = "black_wool"
    """Black Wool (ID: 216)"""

    BLACKSTONE = "blackstone"
    """Blackstone (ID: 1216)"""

    BLACKSTONE_SLAB = "blackstone_slab"
    """Blackstone Slab (ID: 1217)"""

    BLACKSTONE_STAIRS = "blackstone_stairs"
    """Blackstone Stairs (ID: 1218)"""

    BLACKSTONE_WALL = "blackstone_wall"
    """Blackstone Wall (ID: 411)"""

    BLADE_POTTERY_SHERD = "blade_pottery_sherd"
    """Blade Pottery Sherd (ID: 1277)"""

    BLAST_FURNACE = "blast_furnace"
    """Blast Furnace (ID: 1195)"""

    BLAZE_POWDER = "blaze_powder"
    """Blaze Powder (ID: 999)"""

    BLAZE_ROD = "blaze_rod"
    """Blaze Rod (ID: 991)"""

    BLAZE_SPAWN_EGG = "blaze_spawn_egg"
    """Blaze Spawn Egg (ID: 1009)"""

    BLUE_BANNER = "blue_banner"
    """Blue Banner (ID: 1137)"""

    BLUE_BED = "blue_bed"
    """Blue Bed (ID: 972)"""

    BLUE_CANDLE = "blue_candle"
    """Blue Candle (ID: 1241)"""

    BLUE_CARPET = "blue_carpet"
    """Blue Carpet (ID: 456)"""

    BLUE_CONCRETE = "blue_concrete"
    """Blue Concrete (ID: 565)"""

    BLUE_CONCRETE_POWDER = "blue_concrete_powder"
    """Blue Concrete Powder (ID: 581)"""

    BLUE_DYE = "blue_dye"
    """Blue Dye (ID: 952)"""

    BLUE_GLAZED_TERRACOTTA = "blue_glazed_terracotta"
    """Blue Glazed Terracotta (ID: 549)"""

    BLUE_ICE = "blue_ice"
    """Blue Ice (ID: 618)"""

    BLUE_ORCHID = "blue_orchid"
    """Blue Orchid (ID: 219)"""

    BLUE_SHULKER_BOX = "blue_shulker_box"
    """Blue Shulker Box (ID: 533)"""

    BLUE_STAINED_GLASS = "blue_stained_glass"
    """Blue Stained Glass (ID: 481)"""

    BLUE_STAINED_GLASS_PANE = "blue_stained_glass_pane"
    """Blue Stained Glass Pane (ID: 497)"""

    BLUE_TERRACOTTA = "blue_terracotta"
    """Blue Terracotta (ID: 437)"""

    BLUE_WOOL = "blue_wool"
    """Blue Wool (ID: 212)"""

    BONE = "bone"
    """Bone (ID: 958)"""

    BONE_BLOCK = "bone_block"
    """Bone Block (ID: 519)"""

    BONE_MEAL = "bone_meal"
    """Bone Meal (ID: 957)"""

    BOOK = "book"
    """Book (ID: 922)"""

    BOOKSHELF = "bookshelf"
    """Bookshelf (ID: 285)"""

    BOW = "bow"
    """Bow (ID: 797)"""

    BOWL = "bowl"
    """Bowl (ID: 845)"""

    BRAIN_CORAL = "brain_coral"
    """Brain Coral (ID: 599)"""

    BRAIN_CORAL_BLOCK = "brain_coral_block"
    """Brain Coral Block (ID: 594)"""

    BRAIN_CORAL_FAN = "brain_coral_fan"
    """Brain Coral Fan (ID: 609)"""

    BREAD = "bread"
    """Bread (ID: 852)"""

    BREEZE_SPAWN_EGG = "breeze_spawn_egg"
    """Breeze Spawn Egg (ID: 1010)"""

    BREWER_POTTERY_SHERD = "brewer_pottery_sherd"
    """Brewer Pottery Sherd (ID: 1278)"""

    BREWING_STAND = "brewing_stand"
    """Brewing Stand (ID: 1001)"""

    BRICK = "brick"
    """Brick (ID: 918)"""

    BRICK_SLAB = "brick_slab"
    """Brick Slab (ID: 269)"""

    BRICK_STAIRS = "brick_stairs"
    """Brick Stairs (ID: 360)"""

    BRICK_WALL = "brick_wall"
    """Brick Wall (ID: 398)"""

    BRICKS = "bricks"
    """Bricks (ID: 284)"""

    BROWN_BANNER = "brown_banner"
    """Brown Banner (ID: 1138)"""

    BROWN_BED = "brown_bed"
    """Brown Bed (ID: 973)"""

    BROWN_CANDLE = "brown_candle"
    """Brown Candle (ID: 1242)"""

    BROWN_CARPET = "brown_carpet"
    """Brown Carpet (ID: 457)"""

    BROWN_CONCRETE = "brown_concrete"
    """Brown Concrete (ID: 566)"""

    BROWN_CONCRETE_POWDER = "brown_concrete_powder"
    """Brown Concrete Powder (ID: 582)"""

    BROWN_DYE = "brown_dye"
    """Brown Dye (ID: 953)"""

    BROWN_GLAZED_TERRACOTTA = "brown_glazed_terracotta"
    """Brown Glazed Terracotta (ID: 550)"""

    BROWN_MUSHROOM = "brown_mushroom"
    """Brown Mushroom (ID: 233)"""

    BROWN_MUSHROOM_BLOCK = "brown_mushroom_block"
    """Brown Mushroom Block (ID: 351)"""

    BROWN_SHULKER_BOX = "brown_shulker_box"
    """Brown Shulker Box (ID: 534)"""

    BROWN_STAINED_GLASS = "brown_stained_glass"
    """Brown Stained Glass (ID: 482)"""

    BROWN_STAINED_GLASS_PANE = "brown_stained_glass_pane"
    """Brown Stained Glass Pane (ID: 498)"""

    BROWN_TERRACOTTA = "brown_terracotta"
    """Brown Terracotta (ID: 438)"""

    BROWN_WOOL = "brown_wool"
    """Brown Wool (ID: 213)"""

    BRUSH = "brush"
    """Brush (ID: 1256)"""

    BUBBLE_CORAL = "bubble_coral"
    """Bubble Coral (ID: 600)"""

    BUBBLE_CORAL_BLOCK = "bubble_coral_block"
    """Bubble Coral Block (ID: 595)"""

    BUBBLE_CORAL_FAN = "bubble_coral_fan"
    """Bubble Coral Fan (ID: 610)"""

    BUCKET = "bucket"
    """Bucket (ID: 905)"""

    BUDDING_AMETHYST = "budding_amethyst"
    """Budding Amethyst (ID: 86)"""

    BUNDLE = "bundle"
    """Bundle (ID: 927)"""

    BURN_POTTERY_SHERD = "burn_pottery_sherd"
    """Burn Pottery Sherd (ID: 1279)"""

    CACTUS = "cactus"
    """Cactus (ID: 307)"""

    CAKE = "cake"
    """Cake (ID: 960)"""

    CALCITE = "calcite"
    """Calcite (ID: 11)"""

    CALIBRATED_SCULK_SENSOR = "calibrated_sculk_sensor"
    """Calibrated Sculk Sensor (ID: 675)"""

    CAMEL_SPAWN_EGG = "camel_spawn_egg"
    """Camel Spawn Egg (ID: 1012)"""

    CAMPFIRE = "campfire"
    """Campfire (ID: 1206)"""

    CANDLE = "candle"
    """Candle (ID: 1229)"""

    CARROT = "carrot"
    """Carrot (ID: 1090)"""

    CARROT_ON_A_STICK = "carrot_on_a_stick"
    """Carrot on a Stick (ID: 770)"""

    CARTOGRAPHY_TABLE = "cartography_table"
    """Cartography Table (ID: 1196)"""

    CARVED_PUMPKIN = "carved_pumpkin"
    """Carved Pumpkin (ID: 322)"""

    CAT_SPAWN_EGG = "cat_spawn_egg"
    """Cat Spawn Egg (ID: 1011)"""

    CAULDRON = "cauldron"
    """Cauldron (ID: 1002)"""

    CAVE_SPIDER_SPAWN_EGG = "cave_spider_spawn_egg"
    """Cave Spider Spawn Egg (ID: 1013)"""

    CHAIN = "chain"
    """Chain (ID: 355)"""

    CHAIN_COMMAND_BLOCK = "chain_command_block"
    """Chain Command Block (ID: 514)"""

    CHAINMAIL_BOOTS = "chainmail_boots"
    """Chainmail Boots (ID: 860)"""

    CHAINMAIL_CHESTPLATE = "chainmail_chestplate"
    """Chainmail Chestplate (ID: 858)"""

    CHAINMAIL_HELMET = "chainmail_helmet"
    """Chainmail Helmet (ID: 857)"""

    CHAINMAIL_LEGGINGS = "chainmail_leggings"
    """Chainmail Leggings (ID: 859)"""

    CHARCOAL = "charcoal"
    """Charcoal (ID: 800)"""

    CHERRY_BOAT = "cherry_boat"
    """Cherry Boat (ID: 783)"""

    CHERRY_BUTTON = "cherry_button"
    """Cherry Button (ID: 688)"""

    CHERRY_CHEST_BOAT = "cherry_chest_boat"
    """Cherry Boat with Chest (ID: 784)"""

    CHERRY_DOOR = "cherry_door"
    """Cherry Door (ID: 715)"""

    CHERRY_FENCE = "cherry_fence"
    """Cherry Fence (ID: 315)"""

    CHERRY_FENCE_GATE = "cherry_fence_gate"
    """Cherry Fence Gate (ID: 754)"""

    CHERRY_HANGING_SIGN = "cherry_hanging_sign"
    """Cherry Hanging Sign (ID: 899)"""

    CHERRY_LEAVES = "cherry_leaves"
    """Cherry Leaves (ID: 180)"""

    CHERRY_LOG = "cherry_log"
    """Cherry Log (ID: 136)"""

    CHERRY_PLANKS = "cherry_planks"
    """Cherry Planks (ID: 41)"""

    CHERRY_PRESSURE_PLATE = "cherry_pressure_plate"
    """Cherry Pressure Plate (ID: 703)"""

    CHERRY_SAPLING = "cherry_sapling"
    """Cherry Sapling (ID: 53)"""

    CHERRY_SIGN = "cherry_sign"
    """Cherry Sign (ID: 888)"""

    CHERRY_SLAB = "cherry_slab"
    """Cherry Slab (ID: 256)"""

    CHERRY_STAIRS = "cherry_stairs"
    """Cherry Stairs (ID: 387)"""

    CHERRY_TRAPDOOR = "cherry_trapdoor"
    """Cherry Trapdoor (ID: 735)"""

    CHERRY_WOOD = "cherry_wood"
    """Cherry Wood (ID: 170)"""

    CHEST = "chest"
    """Chest (ID: 298)"""

    CHEST_MINECART = "chest_minecart"
    """Minecart with Chest (ID: 766)"""

    CHICKEN = "chicken"
    """Raw Chicken (ID: 987)"""

    CHICKEN_SPAWN_EGG = "chicken_spawn_egg"
    """Chicken Spawn Egg (ID: 1014)"""

    CHIPPED_ANVIL = "chipped_anvil"
    """Chipped Anvil (ID: 419)"""

    CHISELED_BOOKSHELF = "chiseled_bookshelf"
    """Chiseled Bookshelf (ID: 286)"""

    CHISELED_COPPER = "chiseled_copper"
    """Chiseled Copper (ID: 95)"""

    CHISELED_DEEPSLATE = "chiseled_deepslate"
    """Chiseled Deepslate (ID: 349)"""

    CHISELED_NETHER_BRICKS = "chiseled_nether_bricks"
    """Chiseled Nether Bricks (ID: 367)"""

    CHISELED_POLISHED_BLACKSTONE = "chiseled_polished_blackstone"
    """Chiseled Polished Blackstone (ID: 1223)"""

    CHISELED_QUARTZ_BLOCK = "chiseled_quartz_block"
    """Chiseled Quartz Block (ID: 421)"""

    CHISELED_RED_SANDSTONE = "chiseled_red_sandstone"
    """Chiseled Red Sandstone (ID: 510)"""

    CHISELED_SANDSTONE = "chiseled_sandstone"
    """Chiseled Sandstone (ID: 191)"""

    CHISELED_STONE_BRICKS = "chiseled_stone_bricks"
    """Chiseled Stone Bricks (ID: 342)"""

    CHISELED_TUFF = "chiseled_tuff"
    """Chiseled Tuff (ID: 16)"""

    CHISELED_TUFF_BRICKS = "chiseled_tuff_bricks"
    """Chiseled Tuff Bricks (ID: 25)"""

    CHORUS_FLOWER = "chorus_flower"
    """Chorus Flower (ID: 293)"""

    CHORUS_FRUIT = "chorus_fruit"
    """Chorus Fruit (ID: 1143)"""

    CHORUS_PLANT = "chorus_plant"
    """Chorus Plant (ID: 292)"""

    CLAY = "clay"
    """Clay (ID: 308)"""

    CLAY_BALL = "clay_ball"
    """Clay Ball (ID: 919)"""

    CLOCK = "clock"
    """Clock (ID: 929)"""

    COAL = "coal"
    """Coal (ID: 799)"""

    COAL_BLOCK = "coal_block"
    """Block of Coal (ID: 81)"""

    COAL_ORE = "coal_ore"
    """Coal Ore (ID: 62)"""

    COARSE_DIRT = "coarse_dirt"
    """Coarse Dirt (ID: 29)"""

    COAST_ARMOR_TRIM_SMITHING_TEMPLATE = "coast_armor_trim_smithing_template"
    """Smithing Template (ID: 1260)"""

    COBBLED_DEEPSLATE = "cobbled_deepslate"
    """Cobbled Deepslate (ID: 9)"""

    COBBLED_DEEPSLATE_SLAB = "cobbled_deepslate_slab"
    """Cobbled Deepslate Slab (ID: 651)"""

    COBBLED_DEEPSLATE_STAIRS = "cobbled_deepslate_stairs"
    """Cobbled Deepslate Stairs (ID: 634)"""

    COBBLED_DEEPSLATE_WALL = "cobbled_deepslate_wall"
    """Cobbled Deepslate Wall (ID: 414)"""

    COBBLESTONE = "cobblestone"
    """Cobblestone (ID: 35)"""

    COBBLESTONE_SLAB = "cobblestone_slab"
    """Cobblestone Slab (ID: 268)"""

    COBBLESTONE_STAIRS = "cobblestone_stairs"
    """Cobblestone Stairs (ID: 303)"""

    COBBLESTONE_WALL = "cobblestone_wall"
    """Cobblestone Wall (ID: 396)"""

    COBWEB = "cobweb"
    """Cobweb (ID: 193)"""

    COCOA_BEANS = "cocoa_beans"
    """Cocoa Beans (ID: 940)"""

    COD = "cod"
    """Raw Cod (ID: 932)"""

    COD_BUCKET = "cod_bucket"
    """Bucket of Cod (ID: 914)"""

    COD_SPAWN_EGG = "cod_spawn_egg"
    """Cod Spawn Egg (ID: 1015)"""

    COMMAND_BLOCK = "command_block"
    """Command Block (ID: 394)"""

    COMMAND_BLOCK_MINECART = "command_block_minecart"
    """Minecart with Command Block (ID: 1123)"""

    COMPARATOR = "comparator"
    """Redstone Comparator (ID: 660)"""

    COMPASS = "compass"
    """Compass (ID: 925)"""

    COMPOSTER = "composter"
    """Composter (ID: 1192)"""

    CONDUIT = "conduit"
    """Conduit (ID: 619)"""

    COOKED_BEEF = "cooked_beef"
    """Steak (ID: 986)"""

    COOKED_CHICKEN = "cooked_chicken"
    """Cooked Chicken (ID: 988)"""

    COOKED_COD = "cooked_cod"
    """Cooked Cod (ID: 936)"""

    COOKED_MUTTON = "cooked_mutton"
    """Cooked Mutton (ID: 1125)"""

    COOKED_PORKCHOP = "cooked_porkchop"
    """Cooked Porkchop (ID: 879)"""

    COOKED_RABBIT = "cooked_rabbit"
    """Cooked Rabbit (ID: 1112)"""

    COOKED_SALMON = "cooked_salmon"
    """Cooked Salmon (ID: 937)"""

    COOKIE = "cookie"
    """Cookie (ID: 977)"""

    COPPER_BLOCK = "copper_block"
    """Block of Copper (ID: 88)"""

    COPPER_BULB = "copper_bulb"
    """Copper Bulb (ID: 1302)"""

    COPPER_DOOR = "copper_door"
    """Copper Door (ID: 721)"""

    COPPER_GRATE = "copper_grate"
    """Copper Grate (ID: 1294)"""

    COPPER_INGOT = "copper_ingot"
    """Copper Ingot (ID: 809)"""

    COPPER_ORE = "copper_ore"
    """Copper Ore (ID: 66)"""

    COPPER_TRAPDOOR = "copper_trapdoor"
    """Copper Trapdoor (ID: 741)"""

    CORNFLOWER = "cornflower"
    """Cornflower (ID: 227)"""

    COW_SPAWN_EGG = "cow_spawn_egg"
    """Cow Spawn Egg (ID: 1016)"""

    CRACKED_DEEPSLATE_BRICKS = "cracked_deepslate_bricks"
    """Cracked Deepslate Bricks (ID: 346)"""

    CRACKED_DEEPSLATE_TILES = "cracked_deepslate_tiles"
    """Cracked Deepslate Tiles (ID: 348)"""

    CRACKED_NETHER_BRICKS = "cracked_nether_bricks"
    """Cracked Nether Bricks (ID: 366)"""

    CRACKED_POLISHED_BLACKSTONE_BRICKS = "cracked_polished_blackstone_bricks"
    """Cracked Polished Blackstone Bricks (ID: 1227)"""

    CRACKED_STONE_BRICKS = "cracked_stone_bricks"
    """Cracked Stone Bricks (ID: 341)"""

    CRAFTER = "crafter"
    """Crafter (ID: 978)"""

    CRAFTING_TABLE = "crafting_table"
    """Crafting Table (ID: 299)"""

    CREEPER_BANNER_PATTERN = "creeper_banner_pattern"
    """Banner Pattern (ID: 1186)"""

    CREEPER_HEAD = "creeper_head"
    """Creeper Head (ID: 1100)"""

    CREEPER_SPAWN_EGG = "creeper_spawn_egg"
    """Creeper Spawn Egg (ID: 1017)"""

    CRIMSON_BUTTON = "crimson_button"
    """Crimson Button (ID: 692)"""

    CRIMSON_DOOR = "crimson_door"
    """Crimson Door (ID: 719)"""

    CRIMSON_FENCE = "crimson_fence"
    """Crimson Fence (ID: 319)"""

    CRIMSON_FENCE_GATE = "crimson_fence_gate"
    """Crimson Fence Gate (ID: 758)"""

    CRIMSON_FUNGUS = "crimson_fungus"
    """Crimson Fungus (ID: 235)"""

    CRIMSON_HANGING_SIGN = "crimson_hanging_sign"
    """Crimson Hanging Sign (ID: 903)"""

    CRIMSON_HYPHAE = "crimson_hyphae"
    """Crimson Hyphae (ID: 173)"""

    CRIMSON_NYLIUM = "crimson_nylium"
    """Crimson Nylium (ID: 33)"""

    CRIMSON_PLANKS = "crimson_planks"
    """Crimson Planks (ID: 45)"""

    CRIMSON_PRESSURE_PLATE = "crimson_pressure_plate"
    """Crimson Pressure Plate (ID: 707)"""

    CRIMSON_ROOTS = "crimson_roots"
    """Crimson Roots (ID: 237)"""

    CRIMSON_SIGN = "crimson_sign"
    """Crimson Sign (ID: 892)"""

    CRIMSON_SLAB = "crimson_slab"
    """Crimson Slab (ID: 261)"""

    CRIMSON_STAIRS = "crimson_stairs"
    """Crimson Stairs (ID: 392)"""

    CRIMSON_STEM = "crimson_stem"
    """Crimson Stem (ID: 141)"""

    CRIMSON_TRAPDOOR = "crimson_trapdoor"
    """Crimson Trapdoor (ID: 739)"""

    CROSSBOW = "crossbow"
    """Crossbow (ID: 1182)"""

    CRYING_OBSIDIAN = "crying_obsidian"
    """Crying Obsidian (ID: 1215)"""

    CUT_COPPER = "cut_copper"
    """Cut Copper (ID: 99)"""

    CUT_COPPER_SLAB = "cut_copper_slab"
    """Cut Copper Slab (ID: 107)"""

    CUT_COPPER_STAIRS = "cut_copper_stairs"
    """Cut Copper Stairs (ID: 103)"""

    CUT_RED_SANDSTONE = "cut_red_sandstone"
    """Cut Red Sandstone (ID: 511)"""

    CUT_RED_SANDSTONE_SLAB = "cut_red_sandstone_slab"
    """Cut Red Sandstone Slab (ID: 275)"""

    CUT_SANDSTONE = "cut_sandstone"
    """Cut Sandstone (ID: 192)"""

    CUT_SANDSTONE_SLAB = "cut_sandstone_slab"
    """Cut Sandstone Slab (ID: 266)"""

    CYAN_BANNER = "cyan_banner"
    """Cyan Banner (ID: 1135)"""

    CYAN_BED = "cyan_bed"
    """Cyan Bed (ID: 970)"""

    CYAN_CANDLE = "cyan_candle"
    """Cyan Candle (ID: 1239)"""

    CYAN_CARPET = "cyan_carpet"
    """Cyan Carpet (ID: 454)"""

    CYAN_CONCRETE = "cyan_concrete"
    """Cyan Concrete (ID: 563)"""

    CYAN_CONCRETE_POWDER = "cyan_concrete_powder"
    """Cyan Concrete Powder (ID: 579)"""

    CYAN_DYE = "cyan_dye"
    """Cyan Dye (ID: 950)"""

    CYAN_GLAZED_TERRACOTTA = "cyan_glazed_terracotta"
    """Cyan Glazed Terracotta (ID: 547)"""

    CYAN_SHULKER_BOX = "cyan_shulker_box"
    """Cyan Shulker Box (ID: 531)"""

    CYAN_STAINED_GLASS = "cyan_stained_glass"
    """Cyan Stained Glass (ID: 479)"""

    CYAN_STAINED_GLASS_PANE = "cyan_stained_glass_pane"
    """Cyan Stained Glass Pane (ID: 495)"""

    CYAN_TERRACOTTA = "cyan_terracotta"
    """Cyan Terracotta (ID: 435)"""

    CYAN_WOOL = "cyan_wool"
    """Cyan Wool (ID: 210)"""

    DAMAGED_ANVIL = "damaged_anvil"
    """Damaged Anvil (ID: 420)"""

    DANDELION = "dandelion"
    """Dandelion (ID: 217)"""

    DANGER_POTTERY_SHERD = "danger_pottery_sherd"
    """Danger Pottery Sherd (ID: 1280)"""

    DARK_OAK_BOAT = "dark_oak_boat"
    """Dark Oak Boat (ID: 785)"""

    DARK_OAK_BUTTON = "dark_oak_button"
    """Dark Oak Button (ID: 689)"""

    DARK_OAK_CHEST_BOAT = "dark_oak_chest_boat"
    """Dark Oak Boat with Chest (ID: 786)"""

    DARK_OAK_DOOR = "dark_oak_door"
    """Dark Oak Door (ID: 716)"""

    DARK_OAK_FENCE = "dark_oak_fence"
    """Dark Oak Fence (ID: 316)"""

    DARK_OAK_FENCE_GATE = "dark_oak_fence_gate"
    """Dark Oak Fence Gate (ID: 755)"""

    DARK_OAK_HANGING_SIGN = "dark_oak_hanging_sign"
    """Dark Oak Hanging Sign (ID: 900)"""

    DARK_OAK_LEAVES = "dark_oak_leaves"
    """Dark Oak Leaves (ID: 181)"""

    DARK_OAK_LOG = "dark_oak_log"
    """Dark Oak Log (ID: 137)"""

    DARK_OAK_PLANKS = "dark_oak_planks"
    """Dark Oak Planks (ID: 42)"""

    DARK_OAK_PRESSURE_PLATE = "dark_oak_pressure_plate"
    """Dark Oak Pressure Plate (ID: 704)"""

    DARK_OAK_SAPLING = "dark_oak_sapling"
    """Dark Oak Sapling (ID: 54)"""

    DARK_OAK_SIGN = "dark_oak_sign"
    """Dark Oak Sign (ID: 889)"""

    DARK_OAK_SLAB = "dark_oak_slab"
    """Dark Oak Slab (ID: 257)"""

    DARK_OAK_STAIRS = "dark_oak_stairs"
    """Dark Oak Stairs (ID: 388)"""

    DARK_OAK_TRAPDOOR = "dark_oak_trapdoor"
    """Dark Oak Trapdoor (ID: 736)"""

    DARK_OAK_WOOD = "dark_oak_wood"
    """Dark Oak Wood (ID: 171)"""

    DARK_PRISMARINE = "dark_prismarine"
    """Dark Prismarine (ID: 504)"""

    DARK_PRISMARINE_SLAB = "dark_prismarine_slab"
    """Dark Prismarine Slab (ID: 279)"""

    DARK_PRISMARINE_STAIRS = "dark_prismarine_stairs"
    """Dark Prismarine Stairs (ID: 507)"""

    DAYLIGHT_DETECTOR = "daylight_detector"
    """Daylight Detector (ID: 673)"""

    DEAD_BRAIN_CORAL = "dead_brain_coral"
    """Dead Brain Coral (ID: 603)"""

    DEAD_BRAIN_CORAL_BLOCK = "dead_brain_coral_block"
    """Dead Brain Coral Block (ID: 589)"""

    DEAD_BRAIN_CORAL_FAN = "dead_brain_coral_fan"
    """Dead Brain Coral Fan (ID: 614)"""

    DEAD_BUBBLE_CORAL = "dead_bubble_coral"
    """Dead Bubble Coral (ID: 604)"""

    DEAD_BUBBLE_CORAL_BLOCK = "dead_bubble_coral_block"
    """Dead Bubble Coral Block (ID: 590)"""

    DEAD_BUBBLE_CORAL_FAN = "dead_bubble_coral_fan"
    """Dead Bubble Coral Fan (ID: 615)"""

    DEAD_BUSH = "dead_bush"
    """Dead Bush (ID: 198)"""

    DEAD_FIRE_CORAL = "dead_fire_coral"
    """Dead Fire Coral (ID: 605)"""

    DEAD_FIRE_CORAL_BLOCK = "dead_fire_coral_block"
    """Dead Fire Coral Block (ID: 591)"""

    DEAD_FIRE_CORAL_FAN = "dead_fire_coral_fan"
    """Dead Fire Coral Fan (ID: 616)"""

    DEAD_HORN_CORAL = "dead_horn_coral"
    """Dead Horn Coral (ID: 606)"""

    DEAD_HORN_CORAL_BLOCK = "dead_horn_coral_block"
    """Dead Horn Coral Block (ID: 592)"""

    DEAD_HORN_CORAL_FAN = "dead_horn_coral_fan"
    """Dead Horn Coral Fan (ID: 617)"""

    DEAD_TUBE_CORAL = "dead_tube_coral"
    """Dead Tube Coral (ID: 607)"""

    DEAD_TUBE_CORAL_BLOCK = "dead_tube_coral_block"
    """Dead Tube Coral Block (ID: 588)"""

    DEAD_TUBE_CORAL_FAN = "dead_tube_coral_fan"
    """Dead Tube Coral Fan (ID: 613)"""

    DEBUG_STICK = "debug_stick"
    """Debug Stick (ID: 1160)"""

    DECORATED_POT = "decorated_pot"
    """Decorated Pot (ID: 287)"""

    DEEPSLATE = "deepslate"
    """Deepslate (ID: 8)"""

    DEEPSLATE_BRICK_SLAB = "deepslate_brick_slab"
    """Deepslate Brick Slab (ID: 653)"""

    DEEPSLATE_BRICK_STAIRS = "deepslate_brick_stairs"
    """Deepslate Brick Stairs (ID: 636)"""

    DEEPSLATE_BRICK_WALL = "deepslate_brick_wall"
    """Deepslate Brick Wall (ID: 416)"""

    DEEPSLATE_BRICKS = "deepslate_bricks"
    """Deepslate Bricks (ID: 345)"""

    DEEPSLATE_COAL_ORE = "deepslate_coal_ore"
    """Deepslate Coal Ore (ID: 63)"""

    DEEPSLATE_COPPER_ORE = "deepslate_copper_ore"
    """Deepslate Copper Ore (ID: 67)"""

    DEEPSLATE_DIAMOND_ORE = "deepslate_diamond_ore"
    """Deepslate Diamond Ore (ID: 77)"""

    DEEPSLATE_EMERALD_ORE = "deepslate_emerald_ore"
    """Deepslate Emerald Ore (ID: 73)"""

    DEEPSLATE_GOLD_ORE = "deepslate_gold_ore"
    """Deepslate Gold Ore (ID: 69)"""

    DEEPSLATE_IRON_ORE = "deepslate_iron_ore"
    """Deepslate Iron Ore (ID: 65)"""

    DEEPSLATE_LAPIS_ORE = "deepslate_lapis_ore"
    """Deepslate Lapis Lazuli Ore (ID: 75)"""

    DEEPSLATE_REDSTONE_ORE = "deepslate_redstone_ore"
    """Deepslate Redstone Ore (ID: 71)"""

    DEEPSLATE_TILE_SLAB = "deepslate_tile_slab"
    """Deepslate Tile Slab (ID: 654)"""

    DEEPSLATE_TILE_STAIRS = "deepslate_tile_stairs"
    """Deepslate Tile Stairs (ID: 637)"""

    DEEPSLATE_TILE_WALL = "deepslate_tile_wall"
    """Deepslate Tile Wall (ID: 417)"""

    DEEPSLATE_TILES = "deepslate_tiles"
    """Deepslate Tiles (ID: 347)"""

    DETECTOR_RAIL = "detector_rail"
    """Detector Rail (ID: 761)"""

    DIAMOND = "diamond"
    """Diamond (ID: 801)"""

    DIAMOND_AXE = "diamond_axe"
    """Diamond Axe (ID: 837)"""

    DIAMOND_BLOCK = "diamond_block"
    """Block of Diamond (ID: 90)"""

    DIAMOND_BOOTS = "diamond_boots"
    """Diamond Boots (ID: 868)"""

    DIAMOND_CHESTPLATE = "diamond_chestplate"
    """Diamond Chestplate (ID: 866)"""

    DIAMOND_HELMET = "diamond_helmet"
    """Diamond Helmet (ID: 865)"""

    DIAMOND_HOE = "diamond_hoe"
    """Diamond Hoe (ID: 838)"""

    DIAMOND_HORSE_ARMOR = "diamond_horse_armor"
    """Diamond Horse Armor (ID: 1119)"""

    DIAMOND_LEGGINGS = "diamond_leggings"
    """Diamond Leggings (ID: 867)"""

    DIAMOND_ORE = "diamond_ore"
    """Diamond Ore (ID: 76)"""

    DIAMOND_PICKAXE = "diamond_pickaxe"
    """Diamond Pickaxe (ID: 836)"""

    DIAMOND_SHOVEL = "diamond_shovel"
    """Diamond Shovel (ID: 835)"""

    DIAMOND_SWORD = "diamond_sword"
    """Diamond Sword (ID: 834)"""

    DIORITE = "diorite"
    """Diorite (ID: 4)"""

    DIORITE_SLAB = "diorite_slab"
    """Diorite Slab (ID: 650)"""

    DIORITE_STAIRS = "diorite_stairs"
    """Diorite Stairs (ID: 633)"""

    DIORITE_WALL = "diorite_wall"
    """Diorite Wall (ID: 410)"""

    DIRT = "dirt"
    """Dirt (ID: 28)"""

    DIRT_PATH = "dirt_path"
    """Dirt Path (ID: 463)"""

    DISC_FRAGMENT_5 = "disc_fragment_5"
    """Disc Fragment (ID: 1177)"""

    DISPENSER = "dispenser"
    """Dispenser (ID: 667)"""

    DOLPHIN_SPAWN_EGG = "dolphin_spawn_egg"
    """Dolphin Spawn Egg (ID: 1018)"""

    DONKEY_SPAWN_EGG = "donkey_spawn_egg"
    """Donkey Spawn Egg (ID: 1019)"""

    DRAGON_BREATH = "dragon_breath"
    """Dragon's Breath (ID: 1150)"""

    DRAGON_EGG = "dragon_egg"
    """Dragon Egg (ID: 378)"""

    DRAGON_HEAD = "dragon_head"
    """Dragon Head (ID: 1101)"""

    DRIED_KELP = "dried_kelp"
    """Dried Kelp (ID: 982)"""

    DRIED_KELP_BLOCK = "dried_kelp_block"
    """Dried Kelp Block (ID: 920)"""

    DRIPSTONE_BLOCK = "dripstone_block"
    """Dripstone Block (ID: 26)"""

    DROPPER = "dropper"
    """Dropper (ID: 668)"""

    DROWNED_SPAWN_EGG = "drowned_spawn_egg"
    """Drowned Spawn Egg (ID: 1020)"""

    DUNE_ARMOR_TRIM_SMITHING_TEMPLATE = "dune_armor_trim_smithing_template"
    """Smithing Template (ID: 1259)"""

    ECHO_SHARD = "echo_shard"
    """Echo Shard (ID: 1255)"""

    EGG = "egg"
    """Egg (ID: 924)"""

    ELDER_GUARDIAN_SPAWN_EGG = "elder_guardian_spawn_egg"
    """Elder Guardian Spawn Egg (ID: 1021)"""

    ELYTRA = "elytra"
    """Elytra (ID: 772)"""

    EMERALD = "emerald"
    """Emerald (ID: 802)"""

    EMERALD_BLOCK = "emerald_block"
    """Block of Emerald (ID: 381)"""

    EMERALD_ORE = "emerald_ore"
    """Emerald Ore (ID: 72)"""

    ENCHANTED_BOOK = "enchanted_book"
    """Enchanted Book (ID: 1107)"""

    ENCHANTED_GOLDEN_APPLE = "enchanted_golden_apple"
    """Enchanted Golden Apple (ID: 882)"""

    ENCHANTING_TABLE = "enchanting_table"
    """Enchanting Table (ID: 374)"""

    END_CRYSTAL = "end_crystal"
    """End Crystal (ID: 1142)"""

    END_PORTAL_FRAME = "end_portal_frame"
    """End Portal Frame (ID: 375)"""

    END_ROD = "end_rod"
    """End Rod (ID: 291)"""

    END_STONE = "end_stone"
    """End Stone (ID: 376)"""

    END_STONE_BRICK_SLAB = "end_stone_brick_slab"
    """End Stone Brick Slab (ID: 643)"""

    END_STONE_BRICK_STAIRS = "end_stone_brick_stairs"
    """End Stone Brick Stairs (ID: 625)"""

    END_STONE_BRICK_WALL = "end_stone_brick_wall"
    """End Stone Brick Wall (ID: 409)"""

    END_STONE_BRICKS = "end_stone_bricks"
    """End Stone Bricks (ID: 377)"""

    ENDER_CHEST = "ender_chest"
    """Ender Chest (ID: 380)"""

    ENDER_DRAGON_SPAWN_EGG = "ender_dragon_spawn_egg"
    """Ender Dragon Spawn Egg (ID: 1022)"""

    ENDER_EYE = "ender_eye"
    """Eye of Ender (ID: 1003)"""

    ENDER_PEARL = "ender_pearl"
    """Ender Pearl (ID: 990)"""

    ENDERMAN_SPAWN_EGG = "enderman_spawn_egg"
    """Enderman Spawn Egg (ID: 1023)"""

    ENDERMITE_SPAWN_EGG = "endermite_spawn_egg"
    """Endermite Spawn Egg (ID: 1024)"""

    EVOKER_SPAWN_EGG = "evoker_spawn_egg"
    """Evoker Spawn Egg (ID: 1025)"""

    EXPERIENCE_BOTTLE = "experience_bottle"
    """Bottle o' Enchanting (ID: 1083)"""

    EXPLORER_POTTERY_SHERD = "explorer_pottery_sherd"
    """Explorer Pottery Sherd (ID: 1281)"""

    EXPOSED_CHISELED_COPPER = "exposed_chiseled_copper"
    """Exposed Chiseled Copper (ID: 96)"""

    EXPOSED_COPPER = "exposed_copper"
    """Exposed Copper (ID: 92)"""

    EXPOSED_COPPER_BULB = "exposed_copper_bulb"
    """Exposed Copper Bulb (ID: 1303)"""

    EXPOSED_COPPER_DOOR = "exposed_copper_door"
    """Exposed Copper Door (ID: 722)"""

    EXPOSED_COPPER_GRATE = "exposed_copper_grate"
    """Exposed Copper Grate (ID: 1295)"""

    EXPOSED_COPPER_TRAPDOOR = "exposed_copper_trapdoor"
    """Exposed Copper Trapdoor (ID: 742)"""

    EXPOSED_CUT_COPPER = "exposed_cut_copper"
    """Exposed Cut Copper (ID: 100)"""

    EXPOSED_CUT_COPPER_SLAB = "exposed_cut_copper_slab"
    """Exposed Cut Copper Slab (ID: 108)"""

    EXPOSED_CUT_COPPER_STAIRS = "exposed_cut_copper_stairs"
    """Exposed Cut Copper Stairs (ID: 104)"""

    EYE_ARMOR_TRIM_SMITHING_TEMPLATE = "eye_armor_trim_smithing_template"
    """Smithing Template (ID: 1263)"""

    FARMLAND = "farmland"
    """Farmland (ID: 300)"""

    FEATHER = "feather"
    """Feather (ID: 848)"""

    FERMENTED_SPIDER_EYE = "fermented_spider_eye"
    """Fermented Spider Eye (ID: 998)"""

    FERN = "fern"
    """Fern (ID: 195)"""

    FILLED_MAP = "filled_map"
    """Map (ID: 979)"""

    FIRE_CHARGE = "fire_charge"
    """Fire Charge (ID: 1084)"""

    FIRE_CORAL = "fire_coral"
    """Fire Coral (ID: 601)"""

    FIRE_CORAL_BLOCK = "fire_coral_block"
    """Fire Coral Block (ID: 596)"""

    FIRE_CORAL_FAN = "fire_coral_fan"
    """Fire Coral Fan (ID: 611)"""

    FIREWORK_ROCKET = "firework_rocket"
    """Firework Rocket (ID: 1105)"""

    FIREWORK_STAR = "firework_star"
    """Firework Star (ID: 1106)"""

    FISHING_ROD = "fishing_rod"
    """Fishing Rod (ID: 928)"""

    FLETCHING_TABLE = "fletching_table"
    """Fletching Table (ID: 1197)"""

    FLINT = "flint"
    """Flint (ID: 877)"""

    FLINT_AND_STEEL = "flint_and_steel"
    """Flint and Steel (ID: 795)"""

    FLOWER_BANNER_PATTERN = "flower_banner_pattern"
    """Banner Pattern (ID: 1185)"""

    FLOWER_POT = "flower_pot"
    """Flower Pot (ID: 1089)"""

    FLOWERING_AZALEA = "flowering_azalea"
    """Flowering Azalea (ID: 197)"""

    FLOWERING_AZALEA_LEAVES = "flowering_azalea_leaves"
    """Flowering Azalea Leaves (ID: 184)"""

    FOX_SPAWN_EGG = "fox_spawn_egg"
    """Fox Spawn Egg (ID: 1026)"""

    FRIEND_POTTERY_SHERD = "friend_pottery_sherd"
    """Friend Pottery Sherd (ID: 1282)"""

    FROG_SPAWN_EGG = "frog_spawn_egg"
    """Frog Spawn Egg (ID: 1027)"""

    FROGSPAWN = "frogspawn"
    """Frogspawn (ID: 1254)"""

    FURNACE = "furnace"
    """Furnace (ID: 301)"""

    FURNACE_MINECART = "furnace_minecart"
    """Minecart with Furnace (ID: 767)"""

    GHAST_SPAWN_EGG = "ghast_spawn_egg"
    """Ghast Spawn Egg (ID: 1028)"""

    GHAST_TEAR = "ghast_tear"
    """Ghast Tear (ID: 992)"""

    GILDED_BLACKSTONE = "gilded_blackstone"
    """Gilded Blackstone (ID: 1219)"""

    GLASS = "glass"
    """Glass (ID: 187)"""

    GLASS_BOTTLE = "glass_bottle"
    """Glass Bottle (ID: 996)"""

    GLASS_PANE = "glass_pane"
    """Glass Pane (ID: 356)"""

    GLISTERING_MELON_SLICE = "glistering_melon_slice"
    """Glistering Melon Slice (ID: 1004)"""

    GLOBE_BANNER_PATTERN = "globe_banner_pattern"
    """Banner Pattern (ID: 1189)"""

    GLOW_BERRIES = "glow_berries"
    """Glow Berries (ID: 1205)"""

    GLOW_INK_SAC = "glow_ink_sac"
    """Glow Ink Sac (ID: 939)"""

    GLOW_ITEM_FRAME = "glow_item_frame"
    """Glow Item Frame (ID: 1088)"""

    GLOW_LICHEN = "glow_lichen"
    """Glow Lichen (ID: 359)"""

    GLOW_SQUID_SPAWN_EGG = "glow_squid_spawn_egg"
    """Glow Squid Spawn Egg (ID: 1029)"""

    GLOWSTONE = "glowstone"
    """Glowstone (ID: 331)"""

    GLOWSTONE_DUST = "glowstone_dust"
    """Glowstone Dust (ID: 931)"""

    GOAT_HORN = "goat_horn"
    """Goat Horn (ID: 1191)"""

    GOAT_SPAWN_EGG = "goat_spawn_egg"
    """Goat Spawn Egg (ID: 1030)"""

    GOLD_BLOCK = "gold_block"
    """Block of Gold (ID: 89)"""

    GOLD_INGOT = "gold_ingot"
    """Gold Ingot (ID: 811)"""

    GOLD_NUGGET = "gold_nugget"
    """Gold Nugget (ID: 993)"""

    GOLD_ORE = "gold_ore"
    """Gold Ore (ID: 68)"""

    GOLDEN_APPLE = "golden_apple"
    """Golden Apple (ID: 881)"""

    GOLDEN_AXE = "golden_axe"
    """Golden Axe (ID: 827)"""

    GOLDEN_BOOTS = "golden_boots"
    """Golden Boots (ID: 872)"""

    GOLDEN_CARROT = "golden_carrot"
    """Golden Carrot (ID: 1095)"""

    GOLDEN_CHESTPLATE = "golden_chestplate"
    """Golden Chestplate (ID: 870)"""

    GOLDEN_HELMET = "golden_helmet"
    """Golden Helmet (ID: 869)"""

    GOLDEN_HOE = "golden_hoe"
    """Golden Hoe (ID: 828)"""

    GOLDEN_HORSE_ARMOR = "golden_horse_armor"
    """Golden Horse Armor (ID: 1118)"""

    GOLDEN_LEGGINGS = "golden_leggings"
    """Golden Leggings (ID: 871)"""

    GOLDEN_PICKAXE = "golden_pickaxe"
    """Golden Pickaxe (ID: 826)"""

    GOLDEN_SHOVEL = "golden_shovel"
    """Golden Shovel (ID: 825)"""

    GOLDEN_SWORD = "golden_sword"
    """Golden Sword (ID: 824)"""

    GRANITE = "granite"
    """Granite (ID: 2)"""

    GRANITE_SLAB = "granite_slab"
    """Granite Slab (ID: 646)"""

    GRANITE_STAIRS = "granite_stairs"
    """Granite Stairs (ID: 629)"""

    GRANITE_WALL = "granite_wall"
    """Granite Wall (ID: 402)"""

    GRASS_BLOCK = "grass_block"
    """Grass Block (ID: 27)"""

    GRAVEL = "gravel"
    """Gravel (ID: 61)"""

    GRAY_BANNER = "gray_banner"
    """Gray Banner (ID: 1133)"""

    GRAY_BED = "gray_bed"
    """Gray Bed (ID: 968)"""

    GRAY_CANDLE = "gray_candle"
    """Gray Candle (ID: 1237)"""

    GRAY_CARPET = "gray_carpet"
    """Gray Carpet (ID: 452)"""

    GRAY_CONCRETE = "gray_concrete"
    """Gray Concrete (ID: 561)"""

    GRAY_CONCRETE_POWDER = "gray_concrete_powder"
    """Gray Concrete Powder (ID: 577)"""

    GRAY_DYE = "gray_dye"
    """Gray Dye (ID: 948)"""

    GRAY_GLAZED_TERRACOTTA = "gray_glazed_terracotta"
    """Gray Glazed Terracotta (ID: 545)"""

    GRAY_SHULKER_BOX = "gray_shulker_box"
    """Gray Shulker Box (ID: 529)"""

    GRAY_STAINED_GLASS = "gray_stained_glass"
    """Gray Stained Glass (ID: 477)"""

    GRAY_STAINED_GLASS_PANE = "gray_stained_glass_pane"
    """Gray Stained Glass Pane (ID: 493)"""

    GRAY_TERRACOTTA = "gray_terracotta"
    """Gray Terracotta (ID: 433)"""

    GRAY_WOOL = "gray_wool"
    """Gray Wool (ID: 208)"""

    GREEN_BANNER = "green_banner"
    """Green Banner (ID: 1139)"""

    GREEN_BED = "green_bed"
    """Green Bed (ID: 974)"""

    GREEN_CANDLE = "green_candle"
    """Green Candle (ID: 1243)"""

    GREEN_CARPET = "green_carpet"
    """Green Carpet (ID: 458)"""

    GREEN_CONCRETE = "green_concrete"
    """Green Concrete (ID: 567)"""

    GREEN_CONCRETE_POWDER = "green_concrete_powder"
    """Green Concrete Powder (ID: 583)"""

    GREEN_DYE = "green_dye"
    """Green Dye (ID: 954)"""

    GREEN_GLAZED_TERRACOTTA = "green_glazed_terracotta"
    """Green Glazed Terracotta (ID: 551)"""

    GREEN_SHULKER_BOX = "green_shulker_box"
    """Green Shulker Box (ID: 535)"""

    GREEN_STAINED_GLASS = "green_stained_glass"
    """Green Stained Glass (ID: 483)"""

    GREEN_STAINED_GLASS_PANE = "green_stained_glass_pane"
    """Green Stained Glass Pane (ID: 499)"""

    GREEN_TERRACOTTA = "green_terracotta"
    """Green Terracotta (ID: 439)"""

    GREEN_WOOL = "green_wool"
    """Green Wool (ID: 214)"""

    GRINDSTONE = "grindstone"
    """Grindstone (ID: 1198)"""

    GUARDIAN_SPAWN_EGG = "guardian_spawn_egg"
    """Guardian Spawn Egg (ID: 1031)"""

    GUNPOWDER = "gunpowder"
    """Gunpowder (ID: 849)"""

    HANGING_ROOTS = "hanging_roots"
    """Hanging Roots (ID: 247)"""

    HAY_BLOCK = "hay_block"
    """Hay Bale (ID: 444)"""

    HEART_OF_THE_SEA = "heart_of_the_sea"
    """Heart of the Sea (ID: 1181)"""

    HEART_POTTERY_SHERD = "heart_pottery_sherd"
    """Heart Pottery Sherd (ID: 1283)"""

    HEARTBREAK_POTTERY_SHERD = "heartbreak_pottery_sherd"
    """Heartbreak Pottery Sherd (ID: 1284)"""

    HEAVY_WEIGHTED_PRESSURE_PLATE = "heavy_weighted_pressure_plate"
    """Heavy Weighted Pressure Plate (ID: 697)"""

    HOGLIN_SPAWN_EGG = "hoglin_spawn_egg"
    """Hoglin Spawn Egg (ID: 1032)"""

    HONEY_BLOCK = "honey_block"
    """Honey Block (ID: 664)"""

    HONEY_BOTTLE = "honey_bottle"
    """Honey Bottle (ID: 1212)"""

    HONEYCOMB = "honeycomb"
    """Honeycomb (ID: 1209)"""

    HONEYCOMB_BLOCK = "honeycomb_block"
    """Honeycomb Block (ID: 1213)"""

    HOPPER = "hopper"
    """Hopper (ID: 666)"""

    HOPPER_MINECART = "hopper_minecart"
    """Minecart with Hopper (ID: 769)"""

    HORN_CORAL = "horn_coral"
    """Horn Coral (ID: 602)"""

    HORN_CORAL_BLOCK = "horn_coral_block"
    """Horn Coral Block (ID: 597)"""

    HORN_CORAL_FAN = "horn_coral_fan"
    """Horn Coral Fan (ID: 612)"""

    HORSE_SPAWN_EGG = "horse_spawn_egg"
    """Horse Spawn Egg (ID: 1033)"""

    HOST_ARMOR_TRIM_SMITHING_TEMPLATE = "host_armor_trim_smithing_template"
    """Smithing Template (ID: 1273)"""

    HOWL_POTTERY_SHERD = "howl_pottery_sherd"
    """Howl Pottery Sherd (ID: 1285)"""

    HUSK_SPAWN_EGG = "husk_spawn_egg"
    """Husk Spawn Egg (ID: 1034)"""

    ICE = "ice"
    """Ice (ID: 305)"""

    INFESTED_CHISELED_STONE_BRICKS = "infested_chiseled_stone_bricks"
    """Infested Chiseled Stone Bricks (ID: 337)"""

    INFESTED_COBBLESTONE = "infested_cobblestone"
    """Infested Cobblestone (ID: 333)"""

    INFESTED_CRACKED_STONE_BRICKS = "infested_cracked_stone_bricks"
    """Infested Cracked Stone Bricks (ID: 336)"""

    INFESTED_DEEPSLATE = "infested_deepslate"
    """Infested Deepslate (ID: 338)"""

    INFESTED_MOSSY_STONE_BRICKS = "infested_mossy_stone_bricks"
    """Infested Mossy Stone Bricks (ID: 335)"""

    INFESTED_STONE = "infested_stone"
    """Infested Stone (ID: 332)"""

    INFESTED_STONE_BRICKS = "infested_stone_bricks"
    """Infested Stone Bricks (ID: 334)"""

    INK_SAC = "ink_sac"
    """Ink Sac (ID: 938)"""

    IRON_AXE = "iron_axe"
    """Iron Axe (ID: 832)"""

    IRON_BARS = "iron_bars"
    """Iron Bars (ID: 354)"""

    IRON_BLOCK = "iron_block"
    """Block of Iron (ID: 87)"""

    IRON_BOOTS = "iron_boots"
    """Iron Boots (ID: 864)"""

    IRON_CHESTPLATE = "iron_chestplate"
    """Iron Chestplate (ID: 862)"""

    IRON_DOOR = "iron_door"
    """Iron Door (ID: 709)"""

    IRON_GOLEM_SPAWN_EGG = "iron_golem_spawn_egg"
    """Iron Golem Spawn Egg (ID: 1035)"""

    IRON_HELMET = "iron_helmet"
    """Iron Helmet (ID: 861)"""

    IRON_HOE = "iron_hoe"
    """Iron Hoe (ID: 833)"""

    IRON_HORSE_ARMOR = "iron_horse_armor"
    """Iron Horse Armor (ID: 1117)"""

    IRON_INGOT = "iron_ingot"
    """Iron Ingot (ID: 807)"""

    IRON_LEGGINGS = "iron_leggings"
    """Iron Leggings (ID: 863)"""

    IRON_NUGGET = "iron_nugget"
    """Iron Nugget (ID: 1158)"""

    IRON_ORE = "iron_ore"
    """Iron Ore (ID: 64)"""

    IRON_PICKAXE = "iron_pickaxe"
    """Iron Pickaxe (ID: 831)"""

    IRON_SHOVEL = "iron_shovel"
    """Iron Shovel (ID: 830)"""

    IRON_SWORD = "iron_sword"
    """Iron Sword (ID: 829)"""

    IRON_TRAPDOOR = "iron_trapdoor"
    """Iron Trapdoor (ID: 729)"""

    ITEM_FRAME = "item_frame"
    """Item Frame (ID: 1087)"""

    JACK_O_LANTERN = "jack_o_lantern"
    """Jack o'Lantern (ID: 323)"""

    JIGSAW = "jigsaw"
    """Jigsaw Block (ID: 792)"""

    JUKEBOX = "jukebox"
    """Jukebox (ID: 309)"""

    JUNGLE_BOAT = "jungle_boat"
    """Jungle Boat (ID: 779)"""

    JUNGLE_BUTTON = "jungle_button"
    """Jungle Button (ID: 686)"""

    JUNGLE_CHEST_BOAT = "jungle_chest_boat"
    """Jungle Boat with Chest (ID: 780)"""

    JUNGLE_DOOR = "jungle_door"
    """Jungle Door (ID: 713)"""

    JUNGLE_FENCE = "jungle_fence"
    """Jungle Fence (ID: 313)"""

    JUNGLE_FENCE_GATE = "jungle_fence_gate"
    """Jungle Fence Gate (ID: 752)"""

    JUNGLE_HANGING_SIGN = "jungle_hanging_sign"
    """Jungle Hanging Sign (ID: 897)"""

    JUNGLE_LEAVES = "jungle_leaves"
    """Jungle Leaves (ID: 178)"""

    JUNGLE_LOG = "jungle_log"
    """Jungle Log (ID: 134)"""

    JUNGLE_PLANKS = "jungle_planks"
    """Jungle Planks (ID: 39)"""

    JUNGLE_PRESSURE_PLATE = "jungle_pressure_plate"
    """Jungle Pressure Plate (ID: 701)"""

    JUNGLE_SAPLING = "jungle_sapling"
    """Jungle Sapling (ID: 51)"""

    JUNGLE_SIGN = "jungle_sign"
    """Jungle Sign (ID: 886)"""

    JUNGLE_SLAB = "jungle_slab"
    """Jungle Slab (ID: 254)"""

    JUNGLE_STAIRS = "jungle_stairs"
    """Jungle Stairs (ID: 385)"""

    JUNGLE_TRAPDOOR = "jungle_trapdoor"
    """Jungle Trapdoor (ID: 733)"""

    JUNGLE_WOOD = "jungle_wood"
    """Jungle Wood (ID: 168)"""

    KELP = "kelp"
    """Kelp (ID: 243)"""

    KNOWLEDGE_BOOK = "knowledge_book"
    """Knowledge Book (ID: 1159)"""

    LADDER = "ladder"
    """Ladder (ID: 302)"""

    LANTERN = "lantern"
    """Lantern (ID: 1202)"""

    LAPIS_BLOCK = "lapis_block"
    """Block of Lapis Lazuli (ID: 189)"""

    LAPIS_LAZULI = "lapis_lazuli"
    """Lapis Lazuli (ID: 803)"""

    LAPIS_ORE = "lapis_ore"
    """Lapis Lazuli Ore (ID: 74)"""

    LARGE_AMETHYST_BUD = "large_amethyst_bud"
    """Large Amethyst Bud (ID: 1248)"""

    LARGE_FERN = "large_fern"
    """Large Fern (ID: 469)"""

    LAVA_BUCKET = "lava_bucket"
    """Lava Bucket (ID: 907)"""

    LEAD = "lead"
    """Lead (ID: 1121)"""

    LEATHER = "leather"
    """Leather (ID: 910)"""

    LEATHER_BOOTS = "leather_boots"
    """Leather Boots (ID: 856)"""

    LEATHER_CHESTPLATE = "leather_chestplate"
    """Leather Tunic (ID: 854)"""

    LEATHER_HELMET = "leather_helmet"
    """Leather Cap (ID: 853)"""

    LEATHER_HORSE_ARMOR = "leather_horse_armor"
    """Leather Horse Armor (ID: 1120)"""

    LEATHER_LEGGINGS = "leather_leggings"
    """Leather Pants (ID: 855)"""

    LECTERN = "lectern"
    """Lectern (ID: 669)"""

    LEVER = "lever"
    """Lever (ID: 671)"""

    LIGHT = "light"
    """Light (ID: 443)"""

    LIGHT_BLUE_BANNER = "light_blue_banner"
    """Light Blue Banner (ID: 1129)"""

    LIGHT_BLUE_BED = "light_blue_bed"
    """Light Blue Bed (ID: 964)"""

    LIGHT_BLUE_CANDLE = "light_blue_candle"
    """Light Blue Candle (ID: 1233)"""

    LIGHT_BLUE_CARPET = "light_blue_carpet"
    """Light Blue Carpet (ID: 448)"""

    LIGHT_BLUE_CONCRETE = "light_blue_concrete"
    """Light Blue Concrete (ID: 557)"""

    LIGHT_BLUE_CONCRETE_POWDER = "light_blue_concrete_powder"
    """Light Blue Concrete Powder (ID: 573)"""

    LIGHT_BLUE_DYE = "light_blue_dye"
    """Light Blue Dye (ID: 944)"""

    LIGHT_BLUE_GLAZED_TERRACOTTA = "light_blue_glazed_terracotta"
    """Light Blue Glazed Terracotta (ID: 541)"""

    LIGHT_BLUE_SHULKER_BOX = "light_blue_shulker_box"
    """Light Blue Shulker Box (ID: 525)"""

    LIGHT_BLUE_STAINED_GLASS = "light_blue_stained_glass"
    """Light Blue Stained Glass (ID: 473)"""

    LIGHT_BLUE_STAINED_GLASS_PANE = "light_blue_stained_glass_pane"
    """Light Blue Stained Glass Pane (ID: 489)"""

    LIGHT_BLUE_TERRACOTTA = "light_blue_terracotta"
    """Light Blue Terracotta (ID: 429)"""

    LIGHT_BLUE_WOOL = "light_blue_wool"
    """Light Blue Wool (ID: 204)"""

    LIGHT_GRAY_BANNER = "light_gray_banner"
    """Light Gray Banner (ID: 1134)"""

    LIGHT_GRAY_BED = "light_gray_bed"
    """Light Gray Bed (ID: 969)"""

    LIGHT_GRAY_CANDLE = "light_gray_candle"
    """Light Gray Candle (ID: 1238)"""

    LIGHT_GRAY_CARPET = "light_gray_carpet"
    """Light Gray Carpet (ID: 453)"""

    LIGHT_GRAY_CONCRETE = "light_gray_concrete"
    """Light Gray Concrete (ID: 562)"""

    LIGHT_GRAY_CONCRETE_POWDER = "light_gray_concrete_powder"
    """Light Gray Concrete Powder (ID: 578)"""

    LIGHT_GRAY_DYE = "light_gray_dye"
    """Light Gray Dye (ID: 949)"""

    LIGHT_GRAY_GLAZED_TERRACOTTA = "light_gray_glazed_terracotta"
    """Light Gray Glazed Terracotta (ID: 546)"""

    LIGHT_GRAY_SHULKER_BOX = "light_gray_shulker_box"
    """Light Gray Shulker Box (ID: 530)"""

    LIGHT_GRAY_STAINED_GLASS = "light_gray_stained_glass"
    """Light Gray Stained Glass (ID: 478)"""

    LIGHT_GRAY_STAINED_GLASS_PANE = "light_gray_stained_glass_pane"
    """Light Gray Stained Glass Pane (ID: 494)"""

    LIGHT_GRAY_TERRACOTTA = "light_gray_terracotta"
    """Light Gray Terracotta (ID: 434)"""

    LIGHT_GRAY_WOOL = "light_gray_wool"
    """Light Gray Wool (ID: 209)"""

    LIGHT_WEIGHTED_PRESSURE_PLATE = "light_weighted_pressure_plate"
    """Light Weighted Pressure Plate (ID: 696)"""

    LIGHTNING_ROD = "lightning_rod"
    """Lightning Rod (ID: 672)"""

    LILAC = "lilac"
    """Lilac (ID: 465)"""

    LILY_OF_THE_VALLEY = "lily_of_the_valley"
    """Lily of the Valley (ID: 228)"""

    LILY_PAD = "lily_pad"
    """Lily Pad (ID: 364)"""

    LIME_BANNER = "lime_banner"
    """Lime Banner (ID: 1131)"""

    LIME_BED = "lime_bed"
    """Lime Bed (ID: 966)"""

    LIME_CANDLE = "lime_candle"
    """Lime Candle (ID: 1235)"""

    LIME_CARPET = "lime_carpet"
    """Lime Carpet (ID: 450)"""

    LIME_CONCRETE = "lime_concrete"
    """Lime Concrete (ID: 559)"""

    LIME_CONCRETE_POWDER = "lime_concrete_powder"
    """Lime Concrete Powder (ID: 575)"""

    LIME_DYE = "lime_dye"
    """Lime Dye (ID: 946)"""

    LIME_GLAZED_TERRACOTTA = "lime_glazed_terracotta"
    """Lime Glazed Terracotta (ID: 543)"""

    LIME_SHULKER_BOX = "lime_shulker_box"
    """Lime Shulker Box (ID: 527)"""

    LIME_STAINED_GLASS = "lime_stained_glass"
    """Lime Stained Glass (ID: 475)"""

    LIME_STAINED_GLASS_PANE = "lime_stained_glass_pane"
    """Lime Stained Glass Pane (ID: 491)"""

    LIME_TERRACOTTA = "lime_terracotta"
    """Lime Terracotta (ID: 431)"""

    LIME_WOOL = "lime_wool"
    """Lime Wool (ID: 206)"""

    LINGERING_POTION = "lingering_potion"
    """Lingering Potion (ID: 1154)"""

    LLAMA_SPAWN_EGG = "llama_spawn_egg"
    """Llama Spawn Egg (ID: 1036)"""

    LODESTONE = "lodestone"
    """Lodestone (ID: 1214)"""

    LOOM = "loom"
    """Loom (ID: 1184)"""

    MAGENTA_BANNER = "magenta_banner"
    """Magenta Banner (ID: 1128)"""

    MAGENTA_BED = "magenta_bed"
    """Magenta Bed (ID: 963)"""

    MAGENTA_CANDLE = "magenta_candle"
    """Magenta Candle (ID: 1232)"""

    MAGENTA_CARPET = "magenta_carpet"
    """Magenta Carpet (ID: 447)"""

    MAGENTA_CONCRETE = "magenta_concrete"
    """Magenta Concrete (ID: 556)"""

    MAGENTA_CONCRETE_POWDER = "magenta_concrete_powder"
    """Magenta Concrete Powder (ID: 572)"""

    MAGENTA_DYE = "magenta_dye"
    """Magenta Dye (ID: 943)"""

    MAGENTA_GLAZED_TERRACOTTA = "magenta_glazed_terracotta"
    """Magenta Glazed Terracotta (ID: 540)"""

    MAGENTA_SHULKER_BOX = "magenta_shulker_box"
    """Magenta Shulker Box (ID: 524)"""

    MAGENTA_STAINED_GLASS = "magenta_stained_glass"
    """Magenta Stained Glass (ID: 472)"""

    MAGENTA_STAINED_GLASS_PANE = "magenta_stained_glass_pane"
    """Magenta Stained Glass Pane (ID: 488)"""

    MAGENTA_TERRACOTTA = "magenta_terracotta"
    """Magenta Terracotta (ID: 428)"""

    MAGENTA_WOOL = "magenta_wool"
    """Magenta Wool (ID: 203)"""

    MAGMA_BLOCK = "magma_block"
    """Magma Block (ID: 515)"""

    MAGMA_CREAM = "magma_cream"
    """Magma Cream (ID: 1000)"""

    MAGMA_CUBE_SPAWN_EGG = "magma_cube_spawn_egg"
    """Magma Cube Spawn Egg (ID: 1037)"""

    MANGROVE_BOAT = "mangrove_boat"
    """Mangrove Boat (ID: 787)"""

    MANGROVE_BUTTON = "mangrove_button"
    """Mangrove Button (ID: 690)"""

    MANGROVE_CHEST_BOAT = "mangrove_chest_boat"
    """Mangrove Boat with Chest (ID: 788)"""

    MANGROVE_DOOR = "mangrove_door"
    """Mangrove Door (ID: 717)"""

    MANGROVE_FENCE = "mangrove_fence"
    """Mangrove Fence (ID: 317)"""

    MANGROVE_FENCE_GATE = "mangrove_fence_gate"
    """Mangrove Fence Gate (ID: 756)"""

    MANGROVE_HANGING_SIGN = "mangrove_hanging_sign"
    """Mangrove Hanging Sign (ID: 901)"""

    MANGROVE_LEAVES = "mangrove_leaves"
    """Mangrove Leaves (ID: 182)"""

    MANGROVE_LOG = "mangrove_log"
    """Mangrove Log (ID: 138)"""

    MANGROVE_PLANKS = "mangrove_planks"
    """Mangrove Planks (ID: 43)"""

    MANGROVE_PRESSURE_PLATE = "mangrove_pressure_plate"
    """Mangrove Pressure Plate (ID: 705)"""

    MANGROVE_PROPAGULE = "mangrove_propagule"
    """Mangrove Propagule (ID: 55)"""

    MANGROVE_ROOTS = "mangrove_roots"
    """Mangrove Roots (ID: 139)"""

    MANGROVE_SIGN = "mangrove_sign"
    """Mangrove Sign (ID: 890)"""

    MANGROVE_SLAB = "mangrove_slab"
    """Mangrove Slab (ID: 258)"""

    MANGROVE_STAIRS = "mangrove_stairs"
    """Mangrove Stairs (ID: 389)"""

    MANGROVE_TRAPDOOR = "mangrove_trapdoor"
    """Mangrove Trapdoor (ID: 737)"""

    MANGROVE_WOOD = "mangrove_wood"
    """Mangrove Wood (ID: 172)"""

    MAP = "map"
    """Empty Map (ID: 1094)"""

    MEDIUM_AMETHYST_BUD = "medium_amethyst_bud"
    """Medium Amethyst Bud (ID: 1247)"""

    MELON = "melon"
    """Melon (ID: 357)"""

    MELON_SEEDS = "melon_seeds"
    """Melon Seeds (ID: 984)"""

    MELON_SLICE = "melon_slice"
    """Melon Slice (ID: 981)"""

    MILK_BUCKET = "milk_bucket"
    """Milk Bucket (ID: 911)"""

    MINECART = "minecart"
    """Minecart (ID: 765)"""

    MINER_POTTERY_SHERD = "miner_pottery_sherd"
    """Miner Pottery Sherd (ID: 1286)"""

    MOJANG_BANNER_PATTERN = "mojang_banner_pattern"
    """Banner Pattern (ID: 1188)"""

    MOOSHROOM_SPAWN_EGG = "mooshroom_spawn_egg"
    """Mooshroom Spawn Egg (ID: 1038)"""

    MOSS_BLOCK = "moss_block"
    """Moss Block (ID: 246)"""

    MOSS_CARPET = "moss_carpet"
    """Moss Carpet (ID: 244)"""

    MOSSY_COBBLESTONE = "mossy_cobblestone"
    """Mossy Cobblestone (ID: 288)"""

    MOSSY_COBBLESTONE_SLAB = "mossy_cobblestone_slab"
    """Mossy Cobblestone Slab (ID: 642)"""

    MOSSY_COBBLESTONE_STAIRS = "mossy_cobblestone_stairs"
    """Mossy Cobblestone Stairs (ID: 624)"""

    MOSSY_COBBLESTONE_WALL = "mossy_cobblestone_wall"
    """Mossy Cobblestone Wall (ID: 397)"""

    MOSSY_STONE_BRICK_SLAB = "mossy_stone_brick_slab"
    """Mossy Stone Brick Slab (ID: 640)"""

    MOSSY_STONE_BRICK_STAIRS = "mossy_stone_brick_stairs"
    """Mossy Stone Brick Stairs (ID: 622)"""

    MOSSY_STONE_BRICK_WALL = "mossy_stone_brick_wall"
    """Mossy Stone Brick Wall (ID: 401)"""

    MOSSY_STONE_BRICKS = "mossy_stone_bricks"
    """Mossy Stone Bricks (ID: 340)"""

    MOURNER_POTTERY_SHERD = "mourner_pottery_sherd"
    """Mourner Pottery Sherd (ID: 1287)"""

    MUD = "mud"
    """Mud (ID: 32)"""

    MUD_BRICK_SLAB = "mud_brick_slab"
    """Mud Brick Slab (ID: 271)"""

    MUD_BRICK_STAIRS = "mud_brick_stairs"
    """Mud Brick Stairs (ID: 362)"""

    MUD_BRICK_WALL = "mud_brick_wall"
    """Mud Brick Wall (ID: 404)"""

    MUD_BRICKS = "mud_bricks"
    """Mud Bricks (ID: 344)"""

    MUDDY_MANGROVE_ROOTS = "muddy_mangrove_roots"
    """Muddy Mangrove Roots (ID: 140)"""

    MULE_SPAWN_EGG = "mule_spawn_egg"
    """Mule Spawn Egg (ID: 1039)"""

    MUSHROOM_STEM = "mushroom_stem"
    """Mushroom Stem (ID: 353)"""

    MUSHROOM_STEW = "mushroom_stew"
    """Mushroom Stew (ID: 846)"""

    MUSIC_DISC_11 = "music_disc_11"
    """Music Disc (ID: 1171)"""

    MUSIC_DISC_13 = "music_disc_13"
    """Music Disc (ID: 1161)"""

    MUSIC_DISC_5 = "music_disc_5"
    """Music Disc (ID: 1175)"""

    MUSIC_DISC_BLOCKS = "music_disc_blocks"
    """Music Disc (ID: 1163)"""

    MUSIC_DISC_CAT = "music_disc_cat"
    """Music Disc (ID: 1162)"""

    MUSIC_DISC_CHIRP = "music_disc_chirp"
    """Music Disc (ID: 1164)"""

    MUSIC_DISC_FAR = "music_disc_far"
    """Music Disc (ID: 1165)"""

    MUSIC_DISC_MALL = "music_disc_mall"
    """Music Disc (ID: 1166)"""

    MUSIC_DISC_MELLOHI = "music_disc_mellohi"
    """Music Disc (ID: 1167)"""

    MUSIC_DISC_OTHERSIDE = "music_disc_otherside"
    """Music Disc (ID: 1173)"""

    MUSIC_DISC_PIGSTEP = "music_disc_pigstep"
    """Music Disc (ID: 1176)"""

    MUSIC_DISC_RELIC = "music_disc_relic"
    """Music Disc (ID: 1174)"""

    MUSIC_DISC_STAL = "music_disc_stal"
    """Music Disc (ID: 1168)"""

    MUSIC_DISC_STRAD = "music_disc_strad"
    """Music Disc (ID: 1169)"""

    MUSIC_DISC_WAIT = "music_disc_wait"
    """Music Disc (ID: 1172)"""

    MUSIC_DISC_WARD = "music_disc_ward"
    """Music Disc (ID: 1170)"""

    MUTTON = "mutton"
    """Raw Mutton (ID: 1124)"""

    MYCELIUM = "mycelium"
    """Mycelium (ID: 363)"""

    NAME_TAG = "name_tag"
    """Name Tag (ID: 1122)"""

    NAUTILUS_SHELL = "nautilus_shell"
    """Nautilus Shell (ID: 1180)"""

    NETHER_BRICK = "nether_brick"
    """Nether Brick (ID: 1108)"""

    NETHER_BRICK_FENCE = "nether_brick_fence"
    """Nether Brick Fence (ID: 368)"""

    NETHER_BRICK_SLAB = "nether_brick_slab"
    """Nether Brick Slab (ID: 272)"""

    NETHER_BRICK_STAIRS = "nether_brick_stairs"
    """Nether Brick Stairs (ID: 369)"""

    NETHER_BRICK_WALL = "nether_brick_wall"
    """Nether Brick Wall (ID: 405)"""

    NETHER_BRICKS = "nether_bricks"
    """Nether Bricks (ID: 365)"""

    NETHER_GOLD_ORE = "nether_gold_ore"
    """Nether Gold Ore (ID: 78)"""

    NETHER_QUARTZ_ORE = "nether_quartz_ore"
    """Nether Quartz Ore (ID: 79)"""

    NETHER_SPROUTS = "nether_sprouts"
    """Nether Sprouts (ID: 239)"""

    NETHER_STAR = "nether_star"
    """Nether Star (ID: 1103)"""

    NETHER_WART = "nether_wart"
    """Nether Wart (ID: 994)"""

    NETHER_WART_BLOCK = "nether_wart_block"
    """Nether Wart Block (ID: 516)"""

    NETHERITE_AXE = "netherite_axe"
    """Netherite Axe (ID: 842)"""

    NETHERITE_BLOCK = "netherite_block"
    """Block of Netherite (ID: 91)"""

    NETHERITE_BOOTS = "netherite_boots"
    """Netherite Boots (ID: 876)"""

    NETHERITE_CHESTPLATE = "netherite_chestplate"
    """Netherite Chestplate (ID: 874)"""

    NETHERITE_HELMET = "netherite_helmet"
    """Netherite Helmet (ID: 873)"""

    NETHERITE_HOE = "netherite_hoe"
    """Netherite Hoe (ID: 843)"""

    NETHERITE_INGOT = "netherite_ingot"
    """Netherite Ingot (ID: 812)"""

    NETHERITE_LEGGINGS = "netherite_leggings"
    """Netherite Leggings (ID: 875)"""

    NETHERITE_PICKAXE = "netherite_pickaxe"
    """Netherite Pickaxe (ID: 841)"""

    NETHERITE_SCRAP = "netherite_scrap"
    """Netherite Scrap (ID: 813)"""

    NETHERITE_SHOVEL = "netherite_shovel"
    """Netherite Shovel (ID: 840)"""

    NETHERITE_SWORD = "netherite_sword"
    """Netherite Sword (ID: 839)"""

    NETHERITE_UPGRADE_SMITHING_TEMPLATE = "netherite_upgrade_smithing_template"
    """Smithing Template (ID: 1257)"""

    NETHERRACK = "netherrack"
    """Netherrack (ID: 324)"""

    NOTE_BLOCK = "note_block"
    """Note Block (ID: 680)"""

    OAK_BOAT = "oak_boat"
    """Oak Boat (ID: 773)"""

    OAK_BUTTON = "oak_button"
    """Oak Button (ID: 683)"""

    OAK_CHEST_BOAT = "oak_chest_boat"
    """Oak Boat with Chest (ID: 774)"""

    OAK_DOOR = "oak_door"
    """Oak Door (ID: 710)"""

    OAK_FENCE = "oak_fence"
    """Oak Fence (ID: 310)"""

    OAK_FENCE_GATE = "oak_fence_gate"
    """Oak Fence Gate (ID: 749)"""

    OAK_HANGING_SIGN = "oak_hanging_sign"
    """Oak Hanging Sign (ID: 894)"""

    OAK_LEAVES = "oak_leaves"
    """Oak Leaves (ID: 175)"""

    OAK_LOG = "oak_log"
    """Oak Log (ID: 131)"""

    OAK_PLANKS = "oak_planks"
    """Oak Planks (ID: 36)"""

    OAK_PRESSURE_PLATE = "oak_pressure_plate"
    """Oak Pressure Plate (ID: 698)"""

    OAK_SAPLING = "oak_sapling"
    """Oak Sapling (ID: 48)"""

    OAK_SIGN = "oak_sign"
    """Oak Sign (ID: 883)"""

    OAK_SLAB = "oak_slab"
    """Oak Slab (ID: 251)"""

    OAK_STAIRS = "oak_stairs"
    """Oak Stairs (ID: 382)"""

    OAK_TRAPDOOR = "oak_trapdoor"
    """Oak Trapdoor (ID: 730)"""

    OAK_WOOD = "oak_wood"
    """Oak Wood (ID: 165)"""

    OBSERVER = "observer"
    """Observer (ID: 665)"""

    OBSIDIAN = "obsidian"
    """Obsidian (ID: 289)"""

    OCELOT_SPAWN_EGG = "ocelot_spawn_egg"
    """Ocelot Spawn Egg (ID: 1040)"""

    OCHRE_FROGLIGHT = "ochre_froglight"
    """Ochre Froglight (ID: 1251)"""

    ORANGE_BANNER = "orange_banner"
    """Orange Banner (ID: 1127)"""

    ORANGE_BED = "orange_bed"
    """Orange Bed (ID: 962)"""

    ORANGE_CANDLE = "orange_candle"
    """Orange Candle (ID: 1231)"""

    ORANGE_CARPET = "orange_carpet"
    """Orange Carpet (ID: 446)"""

    ORANGE_CONCRETE = "orange_concrete"
    """Orange Concrete (ID: 555)"""

    ORANGE_CONCRETE_POWDER = "orange_concrete_powder"
    """Orange Concrete Powder (ID: 571)"""

    ORANGE_DYE = "orange_dye"
    """Orange Dye (ID: 942)"""

    ORANGE_GLAZED_TERRACOTTA = "orange_glazed_terracotta"
    """Orange Glazed Terracotta (ID: 539)"""

    ORANGE_SHULKER_BOX = "orange_shulker_box"
    """Orange Shulker Box (ID: 523)"""

    ORANGE_STAINED_GLASS = "orange_stained_glass"
    """Orange Stained Glass (ID: 471)"""

    ORANGE_STAINED_GLASS_PANE = "orange_stained_glass_pane"
    """Orange Stained Glass Pane (ID: 487)"""

    ORANGE_TERRACOTTA = "orange_terracotta"
    """Orange Terracotta (ID: 427)"""

    ORANGE_TULIP = "orange_tulip"
    """Orange Tulip (ID: 223)"""

    ORANGE_WOOL = "orange_wool"
    """Orange Wool (ID: 202)"""

    OXEYE_DAISY = "oxeye_daisy"
    """Oxeye Daisy (ID: 226)"""

    OXIDIZED_CHISELED_COPPER = "oxidized_chiseled_copper"
    """Oxidized Chiseled Copper (ID: 98)"""

    OXIDIZED_COPPER = "oxidized_copper"
    """Oxidized Copper (ID: 94)"""

    OXIDIZED_COPPER_BULB = "oxidized_copper_bulb"
    """Oxidized Copper Bulb (ID: 1305)"""

    OXIDIZED_COPPER_DOOR = "oxidized_copper_door"
    """Oxidized Copper Door (ID: 724)"""

    OXIDIZED_COPPER_GRATE = "oxidized_copper_grate"
    """Oxidized Copper Grate (ID: 1297)"""

    OXIDIZED_COPPER_TRAPDOOR = "oxidized_copper_trapdoor"
    """Oxidized Copper Trapdoor (ID: 744)"""

    OXIDIZED_CUT_COPPER = "oxidized_cut_copper"
    """Oxidized Cut Copper (ID: 102)"""

    OXIDIZED_CUT_COPPER_SLAB = "oxidized_cut_copper_slab"
    """Oxidized Cut Copper Slab (ID: 110)"""

    OXIDIZED_CUT_COPPER_STAIRS = "oxidized_cut_copper_stairs"
    """Oxidized Cut Copper Stairs (ID: 106)"""

    PACKED_ICE = "packed_ice"
    """Packed Ice (ID: 462)"""

    PACKED_MUD = "packed_mud"
    """Packed Mud (ID: 343)"""

    PAINTING = "painting"
    """Painting (ID: 880)"""

    PANDA_SPAWN_EGG = "panda_spawn_egg"
    """Panda Spawn Egg (ID: 1041)"""

    PAPER = "paper"
    """Paper (ID: 921)"""

    PARROT_SPAWN_EGG = "parrot_spawn_egg"
    """Parrot Spawn Egg (ID: 1042)"""

    PEARLESCENT_FROGLIGHT = "pearlescent_froglight"
    """Pearlescent Froglight (ID: 1253)"""

    PEONY = "peony"
    """Peony (ID: 467)"""

    PETRIFIED_OAK_SLAB = "petrified_oak_slab"
    """Petrified Oak Slab (ID: 267)"""

    PHANTOM_MEMBRANE = "phantom_membrane"
    """Phantom Membrane (ID: 1179)"""

    PHANTOM_SPAWN_EGG = "phantom_spawn_egg"
    """Phantom Spawn Egg (ID: 1043)"""

    PIG_SPAWN_EGG = "pig_spawn_egg"
    """Pig Spawn Egg (ID: 1044)"""

    PIGLIN_BANNER_PATTERN = "piglin_banner_pattern"
    """Banner Pattern (ID: 1190)"""

    PIGLIN_BRUTE_SPAWN_EGG = "piglin_brute_spawn_egg"
    """Piglin Brute Spawn Egg (ID: 1046)"""

    PIGLIN_HEAD = "piglin_head"
    """Piglin Head (ID: 1102)"""

    PIGLIN_SPAWN_EGG = "piglin_spawn_egg"
    """Piglin Spawn Egg (ID: 1045)"""

    PILLAGER_SPAWN_EGG = "pillager_spawn_egg"
    """Pillager Spawn Egg (ID: 1047)"""

    PINK_BANNER = "pink_banner"
    """Pink Banner (ID: 1132)"""

    PINK_BED = "pink_bed"
    """Pink Bed (ID: 967)"""

    PINK_CANDLE = "pink_candle"
    """Pink Candle (ID: 1236)"""

    PINK_CARPET = "pink_carpet"
    """Pink Carpet (ID: 451)"""

    PINK_CONCRETE = "pink_concrete"
    """Pink Concrete (ID: 560)"""

    PINK_CONCRETE_POWDER = "pink_concrete_powder"
    """Pink Concrete Powder (ID: 576)"""

    PINK_DYE = "pink_dye"
    """Pink Dye (ID: 947)"""

    PINK_GLAZED_TERRACOTTA = "pink_glazed_terracotta"
    """Pink Glazed Terracotta (ID: 544)"""

    PINK_PETALS = "pink_petals"
    """Pink Petals (ID: 245)"""

    PINK_SHULKER_BOX = "pink_shulker_box"
    """Pink Shulker Box (ID: 528)"""

    PINK_STAINED_GLASS = "pink_stained_glass"
    """Pink Stained Glass (ID: 476)"""

    PINK_STAINED_GLASS_PANE = "pink_stained_glass_pane"
    """Pink Stained Glass Pane (ID: 492)"""

    PINK_TERRACOTTA = "pink_terracotta"
    """Pink Terracotta (ID: 432)"""

    PINK_TULIP = "pink_tulip"
    """Pink Tulip (ID: 225)"""

    PINK_WOOL = "pink_wool"
    """Pink Wool (ID: 207)"""

    PISTON = "piston"
    """Piston (ID: 661)"""

    PITCHER_PLANT = "pitcher_plant"
    """Pitcher Plant (ID: 231)"""

    PITCHER_POD = "pitcher_pod"
    """Pitcher Pod (ID: 1146)"""

    PLAYER_HEAD = "player_head"
    """Player Head (ID: 1098)"""

    PLENTY_POTTERY_SHERD = "plenty_pottery_sherd"
    """Plenty Pottery Sherd (ID: 1288)"""

    PODZOL = "podzol"
    """Podzol (ID: 30)"""

    POINTED_DRIPSTONE = "pointed_dripstone"
    """Pointed Dripstone (ID: 1250)"""

    POISONOUS_POTATO = "poisonous_potato"
    """Poisonous Potato (ID: 1093)"""

    POLAR_BEAR_SPAWN_EGG = "polar_bear_spawn_egg"
    """Polar Bear Spawn Egg (ID: 1048)"""

    POLISHED_ANDESITE = "polished_andesite"
    """Polished Andesite (ID: 7)"""

    POLISHED_ANDESITE_SLAB = "polished_andesite_slab"
    """Polished Andesite Slab (ID: 649)"""

    POLISHED_ANDESITE_STAIRS = "polished_andesite_stairs"
    """Polished Andesite Stairs (ID: 632)"""

    POLISHED_BASALT = "polished_basalt"
    """Polished Basalt (ID: 328)"""

    POLISHED_BLACKSTONE = "polished_blackstone"
    """Polished Blackstone (ID: 1220)"""

    POLISHED_BLACKSTONE_BRICK_SLAB = "polished_blackstone_brick_slab"
    """Polished Blackstone Brick Slab (ID: 1225)"""

    POLISHED_BLACKSTONE_BRICK_STAIRS = "polished_blackstone_brick_stairs"
    """Polished Blackstone Brick Stairs (ID: 1226)"""

    POLISHED_BLACKSTONE_BRICK_WALL = "polished_blackstone_brick_wall"
    """Polished Blackstone Brick Wall (ID: 413)"""

    POLISHED_BLACKSTONE_BRICKS = "polished_blackstone_bricks"
    """Polished Blackstone Bricks (ID: 1224)"""

    POLISHED_BLACKSTONE_BUTTON = "polished_blackstone_button"
    """Polished Blackstone Button (ID: 682)"""

    POLISHED_BLACKSTONE_PRESSURE_PLATE = "polished_blackstone_pressure_plate"
    """Polished Blackstone Pressure Plate (ID: 695)"""

    POLISHED_BLACKSTONE_SLAB = "polished_blackstone_slab"
    """Polished Blackstone Slab (ID: 1221)"""

    POLISHED_BLACKSTONE_STAIRS = "polished_blackstone_stairs"
    """Polished Blackstone Stairs (ID: 1222)"""

    POLISHED_BLACKSTONE_WALL = "polished_blackstone_wall"
    """Polished Blackstone Wall (ID: 412)"""

    POLISHED_DEEPSLATE = "polished_deepslate"
    """Polished Deepslate (ID: 10)"""

    POLISHED_DEEPSLATE_SLAB = "polished_deepslate_slab"
    """Polished Deepslate Slab (ID: 652)"""

    POLISHED_DEEPSLATE_STAIRS = "polished_deepslate_stairs"
    """Polished Deepslate Stairs (ID: 635)"""

    POLISHED_DEEPSLATE_WALL = "polished_deepslate_wall"
    """Polished Deepslate Wall (ID: 415)"""

    POLISHED_DIORITE = "polished_diorite"
    """Polished Diorite (ID: 5)"""

    POLISHED_DIORITE_SLAB = "polished_diorite_slab"
    """Polished Diorite Slab (ID: 641)"""

    POLISHED_DIORITE_STAIRS = "polished_diorite_stairs"
    """Polished Diorite Stairs (ID: 623)"""

    POLISHED_GRANITE = "polished_granite"
    """Polished Granite (ID: 3)"""

    POLISHED_GRANITE_SLAB = "polished_granite_slab"
    """Polished Granite Slab (ID: 638)"""

    POLISHED_GRANITE_STAIRS = "polished_granite_stairs"
    """Polished Granite Stairs (ID: 620)"""

    POLISHED_TUFF = "polished_tuff"
    """Polished Tuff (ID: 17)"""

    POLISHED_TUFF_SLAB = "polished_tuff_slab"
    """Polished Tuff Slab (ID: 18)"""

    POLISHED_TUFF_STAIRS = "polished_tuff_stairs"
    """Polished Tuff Stairs (ID: 19)"""

    POLISHED_TUFF_WALL = "polished_tuff_wall"
    """Polished Tuff Wall (ID: 20)"""

    POPPED_CHORUS_FRUIT = "popped_chorus_fruit"
    """Popped Chorus Fruit (ID: 1144)"""

    POPPY = "poppy"
    """Poppy (ID: 218)"""

    PORKCHOP = "porkchop"
    """Raw Porkchop (ID: 878)"""

    POTATO = "potato"
    """Potato (ID: 1091)"""

    POTION = "potion"
    """Potion (ID: 995)"""

    POWDER_SNOW_BUCKET = "powder_snow_bucket"
    """Powder Snow Bucket (ID: 908)"""

    POWERED_RAIL = "powered_rail"
    """Powered Rail (ID: 760)"""

    PRISMARINE = "prismarine"
    """Prismarine (ID: 502)"""

    PRISMARINE_BRICK_SLAB = "prismarine_brick_slab"
    """Prismarine Brick Slab (ID: 278)"""

    PRISMARINE_BRICK_STAIRS = "prismarine_brick_stairs"
    """Prismarine Brick Stairs (ID: 506)"""

    PRISMARINE_BRICKS = "prismarine_bricks"
    """Prismarine Bricks (ID: 503)"""

    PRISMARINE_CRYSTALS = "prismarine_crystals"
    """Prismarine Crystals (ID: 1110)"""

    PRISMARINE_SHARD = "prismarine_shard"
    """Prismarine Shard (ID: 1109)"""

    PRISMARINE_SLAB = "prismarine_slab"
    """Prismarine Slab (ID: 277)"""

    PRISMARINE_STAIRS = "prismarine_stairs"
    """Prismarine Stairs (ID: 505)"""

    PRISMARINE_WALL = "prismarine_wall"
    """Prismarine Wall (ID: 399)"""

    PRIZE_POTTERY_SHERD = "prize_pottery_sherd"
    """Prize Pottery Sherd (ID: 1289)"""

    PUFFERFISH = "pufferfish"
    """Pufferfish (ID: 935)"""

    PUFFERFISH_BUCKET = "pufferfish_bucket"
    """Bucket of Pufferfish (ID: 912)"""

    PUFFERFISH_SPAWN_EGG = "pufferfish_spawn_egg"
    """Pufferfish Spawn Egg (ID: 1049)"""

    PUMPKIN = "pumpkin"
    """Pumpkin (ID: 321)"""

    PUMPKIN_PIE = "pumpkin_pie"
    """Pumpkin Pie (ID: 1104)"""

    PUMPKIN_SEEDS = "pumpkin_seeds"
    """Pumpkin Seeds (ID: 983)"""

    PURPLE_BANNER = "purple_banner"
    """Purple Banner (ID: 1136)"""

    PURPLE_BED = "purple_bed"
    """Purple Bed (ID: 971)"""

    PURPLE_CANDLE = "purple_candle"
    """Purple Candle (ID: 1240)"""

    PURPLE_CARPET = "purple_carpet"
    """Purple Carpet (ID: 455)"""

    PURPLE_CONCRETE = "purple_concrete"
    """Purple Concrete (ID: 564)"""

    PURPLE_CONCRETE_POWDER = "purple_concrete_powder"
    """Purple Concrete Powder (ID: 580)"""

    PURPLE_DYE = "purple_dye"
    """Purple Dye (ID: 951)"""

    PURPLE_GLAZED_TERRACOTTA = "purple_glazed_terracotta"
    """Purple Glazed Terracotta (ID: 548)"""

    PURPLE_SHULKER_BOX = "purple_shulker_box"
    """Purple Shulker Box (ID: 532)"""

    PURPLE_STAINED_GLASS = "purple_stained_glass"
    """Purple Stained Glass (ID: 480)"""

    PURPLE_STAINED_GLASS_PANE = "purple_stained_glass_pane"
    """Purple Stained Glass Pane (ID: 496)"""

    PURPLE_TERRACOTTA = "purple_terracotta"
    """Purple Terracotta (ID: 436)"""

    PURPLE_WOOL = "purple_wool"
    """Purple Wool (ID: 211)"""

    PURPUR_BLOCK = "purpur_block"
    """Purpur Block (ID: 294)"""

    PURPUR_PILLAR = "purpur_pillar"
    """Purpur Pillar (ID: 295)"""

    PURPUR_SLAB = "purpur_slab"
    """Purpur Slab (ID: 276)"""

    PURPUR_STAIRS = "purpur_stairs"
    """Purpur Stairs (ID: 296)"""

    QUARTZ = "quartz"
    """Nether Quartz (ID: 804)"""

    QUARTZ_BLOCK = "quartz_block"
    """Block of Quartz (ID: 422)"""

    QUARTZ_BRICKS = "quartz_bricks"
    """Quartz Bricks (ID: 423)"""

    QUARTZ_PILLAR = "quartz_pillar"
    """Quartz Pillar (ID: 424)"""

    QUARTZ_SLAB = "quartz_slab"
    """Quartz Slab (ID: 273)"""

    QUARTZ_STAIRS = "quartz_stairs"
    """Quartz Stairs (ID: 425)"""

    RABBIT = "rabbit"
    """Raw Rabbit (ID: 1111)"""

    RABBIT_FOOT = "rabbit_foot"
    """Rabbit's Foot (ID: 1114)"""

    RABBIT_HIDE = "rabbit_hide"
    """Rabbit Hide (ID: 1115)"""

    RABBIT_SPAWN_EGG = "rabbit_spawn_egg"
    """Rabbit Spawn Egg (ID: 1050)"""

    RABBIT_STEW = "rabbit_stew"
    """Rabbit Stew (ID: 1113)"""

    RAIL = "rail"
    """Rail (ID: 762)"""

    RAISER_ARMOR_TRIM_SMITHING_TEMPLATE = "raiser_armor_trim_smithing_template"
    """Smithing Template (ID: 1272)"""

    RAVAGER_SPAWN_EGG = "ravager_spawn_egg"
    """Ravager Spawn Egg (ID: 1051)"""

    RAW_COPPER = "raw_copper"
    """Raw Copper (ID: 808)"""

    RAW_COPPER_BLOCK = "raw_copper_block"
    """Block of Raw Copper (ID: 83)"""

    RAW_GOLD = "raw_gold"
    """Raw Gold (ID: 810)"""

    RAW_GOLD_BLOCK = "raw_gold_block"
    """Block of Raw Gold (ID: 84)"""

    RAW_IRON = "raw_iron"
    """Raw Iron (ID: 806)"""

    RAW_IRON_BLOCK = "raw_iron_block"
    """Block of Raw Iron (ID: 82)"""

    RECOVERY_COMPASS = "recovery_compass"
    """Recovery Compass (ID: 926)"""

    RED_BANNER = "red_banner"
    """Red Banner (ID: 1140)"""

    RED_BED = "red_bed"
    """Red Bed (ID: 975)"""

    RED_CANDLE = "red_candle"
    """Red Candle (ID: 1244)"""

    RED_CARPET = "red_carpet"
    """Red Carpet (ID: 459)"""

    RED_CONCRETE = "red_concrete"
    """Red Concrete (ID: 568)"""

    RED_CONCRETE_POWDER = "red_concrete_powder"
    """Red Concrete Powder (ID: 584)"""

    RED_DYE = "red_dye"
    """Red Dye (ID: 955)"""

    RED_GLAZED_TERRACOTTA = "red_glazed_terracotta"
    """Red Glazed Terracotta (ID: 552)"""

    RED_MUSHROOM = "red_mushroom"
    """Red Mushroom (ID: 234)"""

    RED_MUSHROOM_BLOCK = "red_mushroom_block"
    """Red Mushroom Block (ID: 352)"""

    RED_NETHER_BRICK_SLAB = "red_nether_brick_slab"
    """Red Nether Brick Slab (ID: 648)"""

    RED_NETHER_BRICK_STAIRS = "red_nether_brick_stairs"
    """Red Nether Brick Stairs (ID: 631)"""

    RED_NETHER_BRICK_WALL = "red_nether_brick_wall"
    """Red Nether Brick Wall (ID: 407)"""

    RED_NETHER_BRICKS = "red_nether_bricks"
    """Red Nether Bricks (ID: 518)"""

    RED_SAND = "red_sand"
    """Red Sand (ID: 60)"""

    RED_SANDSTONE = "red_sandstone"
    """Red Sandstone (ID: 509)"""

    RED_SANDSTONE_SLAB = "red_sandstone_slab"
    """Red Sandstone Slab (ID: 274)"""

    RED_SANDSTONE_STAIRS = "red_sandstone_stairs"
    """Red Sandstone Stairs (ID: 512)"""

    RED_SANDSTONE_WALL = "red_sandstone_wall"
    """Red Sandstone Wall (ID: 400)"""

    RED_SHULKER_BOX = "red_shulker_box"
    """Red Shulker Box (ID: 536)"""

    RED_STAINED_GLASS = "red_stained_glass"
    """Red Stained Glass (ID: 484)"""

    RED_STAINED_GLASS_PANE = "red_stained_glass_pane"
    """Red Stained Glass Pane (ID: 500)"""

    RED_TERRACOTTA = "red_terracotta"
    """Red Terracotta (ID: 440)"""

    RED_TULIP = "red_tulip"
    """Red Tulip (ID: 222)"""

    RED_WOOL = "red_wool"
    """Red Wool (ID: 215)"""

    REDSTONE = "redstone"
    """Redstone Dust (ID: 656)"""

    REDSTONE_BLOCK = "redstone_block"
    """Block of Redstone (ID: 658)"""

    REDSTONE_LAMP = "redstone_lamp"
    """Redstone Lamp (ID: 679)"""

    REDSTONE_ORE = "redstone_ore"
    """Redstone Ore (ID: 70)"""

    REDSTONE_TORCH = "redstone_torch"
    """Redstone Torch (ID: 657)"""

    REINFORCED_DEEPSLATE = "reinforced_deepslate"
    """Reinforced Deepslate (ID: 350)"""

    REPEATER = "repeater"
    """Redstone Repeater (ID: 659)"""

    REPEATING_COMMAND_BLOCK = "repeating_command_block"
    """Repeating Command Block (ID: 513)"""

    RESPAWN_ANCHOR = "respawn_anchor"
    """Respawn Anchor (ID: 1228)"""

    RIB_ARMOR_TRIM_SMITHING_TEMPLATE = "rib_armor_trim_smithing_template"
    """Smithing Template (ID: 1267)"""

    ROOTED_DIRT = "rooted_dirt"
    """Rooted Dirt (ID: 31)"""

    ROSE_BUSH = "rose_bush"
    """Rose Bush (ID: 466)"""

    ROTTEN_FLESH = "rotten_flesh"
    """Rotten Flesh (ID: 989)"""

    SADDLE = "saddle"
    """Saddle (ID: 764)"""

    SALMON = "salmon"
    """Raw Salmon (ID: 933)"""

    SALMON_BUCKET = "salmon_bucket"
    """Bucket of Salmon (ID: 913)"""

    SALMON_SPAWN_EGG = "salmon_spawn_egg"
    """Salmon Spawn Egg (ID: 1052)"""

    SAND = "sand"
    """Sand (ID: 57)"""

    SANDSTONE = "sandstone"
    """Sandstone (ID: 190)"""

    SANDSTONE_SLAB = "sandstone_slab"
    """Sandstone Slab (ID: 265)"""

    SANDSTONE_STAIRS = "sandstone_stairs"
    """Sandstone Stairs (ID: 379)"""

    SANDSTONE_WALL = "sandstone_wall"
    """Sandstone Wall (ID: 408)"""

    SCAFFOLDING = "scaffolding"
    """Scaffolding (ID: 655)"""

    SCULK = "sculk"
    """Sculk (ID: 370)"""

    SCULK_CATALYST = "sculk_catalyst"
    """Sculk Catalyst (ID: 372)"""

    SCULK_SENSOR = "sculk_sensor"
    """Sculk Sensor (ID: 674)"""

    SCULK_SHRIEKER = "sculk_shrieker"
    """Sculk Shrieker (ID: 373)"""

    SCULK_VEIN = "sculk_vein"
    """Sculk Vein (ID: 371)"""

    SCUTE = "scute"
    """Scute (ID: 794)"""

    SEA_LANTERN = "sea_lantern"
    """Sea Lantern (ID: 508)"""

    SEA_PICKLE = "sea_pickle"
    """Sea Pickle (ID: 200)"""

    SEAGRASS = "seagrass"
    """Seagrass (ID: 199)"""

    SENTRY_ARMOR_TRIM_SMITHING_TEMPLATE = "sentry_armor_trim_smithing_template"
    """Smithing Template (ID: 1258)"""

    SHAPER_ARMOR_TRIM_SMITHING_TEMPLATE = "shaper_armor_trim_smithing_template"
    """Smithing Template (ID: 1270)"""

    SHEAF_POTTERY_SHERD = "sheaf_pottery_sherd"
    """Sheaf Pottery Sherd (ID: 1290)"""

    SHEARS = "shears"
    """Shears (ID: 980)"""

    SHEEP_SPAWN_EGG = "sheep_spawn_egg"
    """Sheep Spawn Egg (ID: 1053)"""

    SHELTER_POTTERY_SHERD = "shelter_pottery_sherd"
    """Shelter Pottery Sherd (ID: 1291)"""

    SHIELD = "shield"
    """Shield (ID: 1155)"""

    SHORT_GRASS = "short_grass"
    """Short Grass (ID: 194)"""

    SHROOMLIGHT = "shroomlight"
    """Shroomlight (ID: 1208)"""

    SHULKER_BOX = "shulker_box"
    """Shulker Box (ID: 521)"""

    SHULKER_SHELL = "shulker_shell"
    """Shulker Shell (ID: 1157)"""

    SHULKER_SPAWN_EGG = "shulker_spawn_egg"
    """Shulker Spawn Egg (ID: 1054)"""

    SILENCE_ARMOR_TRIM_SMITHING_TEMPLATE = "silence_armor_trim_smithing_template"
    """Smithing Template (ID: 1271)"""

    SILVERFISH_SPAWN_EGG = "silverfish_spawn_egg"
    """Silverfish Spawn Egg (ID: 1055)"""

    SKELETON_HORSE_SPAWN_EGG = "skeleton_horse_spawn_egg"
    """Skeleton Horse Spawn Egg (ID: 1057)"""

    SKELETON_SKULL = "skeleton_skull"
    """Skeleton Skull (ID: 1096)"""

    SKELETON_SPAWN_EGG = "skeleton_spawn_egg"
    """Skeleton Spawn Egg (ID: 1056)"""

    SKULL_BANNER_PATTERN = "skull_banner_pattern"
    """Banner Pattern (ID: 1187)"""

    SKULL_POTTERY_SHERD = "skull_pottery_sherd"
    """Skull Pottery Sherd (ID: 1292)"""

    SLIME_BALL = "slime_ball"
    """Slimeball (ID: 923)"""

    SLIME_BLOCK = "slime_block"
    """Slime Block (ID: 663)"""

    SLIME_SPAWN_EGG = "slime_spawn_egg"
    """Slime Spawn Egg (ID: 1058)"""

    SMALL_AMETHYST_BUD = "small_amethyst_bud"
    """Small Amethyst Bud (ID: 1246)"""

    SMALL_DRIPLEAF = "small_dripleaf"
    """Small Dripleaf (ID: 249)"""

    SMITHING_TABLE = "smithing_table"
    """Smithing Table (ID: 1199)"""

    SMOKER = "smoker"
    """Smoker (ID: 1194)"""

    SMOOTH_BASALT = "smooth_basalt"
    """Smooth Basalt (ID: 329)"""

    SMOOTH_QUARTZ = "smooth_quartz"
    """Smooth Quartz Block (ID: 280)"""

    SMOOTH_QUARTZ_SLAB = "smooth_quartz_slab"
    """Smooth Quartz Slab (ID: 645)"""

    SMOOTH_QUARTZ_STAIRS = "smooth_quartz_stairs"
    """Smooth Quartz Stairs (ID: 628)"""

    SMOOTH_RED_SANDSTONE = "smooth_red_sandstone"
    """Smooth Red Sandstone (ID: 281)"""

    SMOOTH_RED_SANDSTONE_SLAB = "smooth_red_sandstone_slab"
    """Smooth Red Sandstone Slab (ID: 639)"""

    SMOOTH_RED_SANDSTONE_STAIRS = "smooth_red_sandstone_stairs"
    """Smooth Red Sandstone Stairs (ID: 621)"""

    SMOOTH_SANDSTONE = "smooth_sandstone"
    """Smooth Sandstone (ID: 282)"""

    SMOOTH_SANDSTONE_SLAB = "smooth_sandstone_slab"
    """Smooth Sandstone Slab (ID: 644)"""

    SMOOTH_SANDSTONE_STAIRS = "smooth_sandstone_stairs"
    """Smooth Sandstone Stairs (ID: 627)"""

    SMOOTH_STONE = "smooth_stone"
    """Smooth Stone (ID: 283)"""

    SMOOTH_STONE_SLAB = "smooth_stone_slab"
    """Smooth Stone Slab (ID: 264)"""

    SNIFFER_EGG = "sniffer_egg"
    """Sniffer Egg (ID: 587)"""

    SNIFFER_SPAWN_EGG = "sniffer_spawn_egg"
    """Sniffer Spawn Egg (ID: 1059)"""

    SNORT_POTTERY_SHERD = "snort_pottery_sherd"
    """Snort Pottery Sherd (ID: 1293)"""

    SNOUT_ARMOR_TRIM_SMITHING_TEMPLATE = "snout_armor_trim_smithing_template"
    """Smithing Template (ID: 1266)"""

    SNOW = "snow"
    """Snow (ID: 304)"""

    SNOW_BLOCK = "snow_block"
    """Snow Block (ID: 306)"""

    SNOW_GOLEM_SPAWN_EGG = "snow_golem_spawn_egg"
    """Snow Golem Spawn Egg (ID: 1060)"""

    SNOWBALL = "snowball"
    """Snowball (ID: 909)"""

    SOUL_CAMPFIRE = "soul_campfire"
    """Soul Campfire (ID: 1207)"""

    SOUL_LANTERN = "soul_lantern"
    """Soul Lantern (ID: 1203)"""

    SOUL_SAND = "soul_sand"
    """Soul Sand (ID: 325)"""

    SOUL_SOIL = "soul_soil"
    """Soul Soil (ID: 326)"""

    SOUL_TORCH = "soul_torch"
    """Soul Torch (ID: 330)"""

    SPAWNER = "spawner"
    """Monster Spawner (ID: 297)"""

    SPECTRAL_ARROW = "spectral_arrow"
    """Spectral Arrow (ID: 1152)"""

    SPIDER_EYE = "spider_eye"
    """Spider Eye (ID: 997)"""

    SPIDER_SPAWN_EGG = "spider_spawn_egg"
    """Spider Spawn Egg (ID: 1061)"""

    SPIRE_ARMOR_TRIM_SMITHING_TEMPLATE = "spire_armor_trim_smithing_template"
    """Smithing Template (ID: 1268)"""

    SPLASH_POTION = "splash_potion"
    """Splash Potion (ID: 1151)"""

    SPONGE = "sponge"
    """Sponge (ID: 185)"""

    SPORE_BLOSSOM = "spore_blossom"
    """Spore Blossom (ID: 232)"""

    SPRUCE_BOAT = "spruce_boat"
    """Spruce Boat (ID: 775)"""

    SPRUCE_BUTTON = "spruce_button"
    """Spruce Button (ID: 684)"""

    SPRUCE_CHEST_BOAT = "spruce_chest_boat"
    """Spruce Boat with Chest (ID: 776)"""

    SPRUCE_DOOR = "spruce_door"
    """Spruce Door (ID: 711)"""

    SPRUCE_FENCE = "spruce_fence"
    """Spruce Fence (ID: 311)"""

    SPRUCE_FENCE_GATE = "spruce_fence_gate"
    """Spruce Fence Gate (ID: 750)"""

    SPRUCE_HANGING_SIGN = "spruce_hanging_sign"
    """Spruce Hanging Sign (ID: 895)"""

    SPRUCE_LEAVES = "spruce_leaves"
    """Spruce Leaves (ID: 176)"""

    SPRUCE_LOG = "spruce_log"
    """Spruce Log (ID: 132)"""

    SPRUCE_PLANKS = "spruce_planks"
    """Spruce Planks (ID: 37)"""

    SPRUCE_PRESSURE_PLATE = "spruce_pressure_plate"
    """Spruce Pressure Plate (ID: 699)"""

    SPRUCE_SAPLING = "spruce_sapling"
    """Spruce Sapling (ID: 49)"""

    SPRUCE_SIGN = "spruce_sign"
    """Spruce Sign (ID: 884)"""

    SPRUCE_SLAB = "spruce_slab"
    """Spruce Slab (ID: 252)"""

    SPRUCE_STAIRS = "spruce_stairs"
    """Spruce Stairs (ID: 383)"""

    SPRUCE_TRAPDOOR = "spruce_trapdoor"
    """Spruce Trapdoor (ID: 731)"""

    SPRUCE_WOOD = "spruce_wood"
    """Spruce Wood (ID: 166)"""

    SPYGLASS = "spyglass"
    """Spyglass (ID: 930)"""

    SQUID_SPAWN_EGG = "squid_spawn_egg"
    """Squid Spawn Egg (ID: 1062)"""

    STICK = "stick"
    """Stick (ID: 844)"""

    STICKY_PISTON = "sticky_piston"
    """Sticky Piston (ID: 662)"""

    STONE = "stone"
    """Stone (ID: 1)"""

    STONE_AXE = "stone_axe"
    """Stone Axe (ID: 822)"""

    STONE_BRICK_SLAB = "stone_brick_slab"
    """Stone Brick Slab (ID: 270)"""

    STONE_BRICK_STAIRS = "stone_brick_stairs"
    """Stone Brick Stairs (ID: 361)"""

    STONE_BRICK_WALL = "stone_brick_wall"
    """Stone Brick Wall (ID: 403)"""

    STONE_BRICKS = "stone_bricks"
    """Stone Bricks (ID: 339)"""

    STONE_BUTTON = "stone_button"
    """Stone Button (ID: 681)"""

    STONE_HOE = "stone_hoe"
    """Stone Hoe (ID: 823)"""

    STONE_PICKAXE = "stone_pickaxe"
    """Stone Pickaxe (ID: 821)"""

    STONE_PRESSURE_PLATE = "stone_pressure_plate"
    """Stone Pressure Plate (ID: 694)"""

    STONE_SHOVEL = "stone_shovel"
    """Stone Shovel (ID: 820)"""

    STONE_SLAB = "stone_slab"
    """Stone Slab (ID: 263)"""

    STONE_STAIRS = "stone_stairs"
    """Stone Stairs (ID: 626)"""

    STONE_SWORD = "stone_sword"
    """Stone Sword (ID: 819)"""

    STONECUTTER = "stonecutter"
    """Stonecutter (ID: 1200)"""

    STRAY_SPAWN_EGG = "stray_spawn_egg"
    """Stray Spawn Egg (ID: 1063)"""

    STRIDER_SPAWN_EGG = "strider_spawn_egg"
    """Strider Spawn Egg (ID: 1064)"""

    STRING = "string"
    """String (ID: 847)"""

    STRIPPED_ACACIA_LOG = "stripped_acacia_log"
    """Stripped Acacia Log (ID: 148)"""

    STRIPPED_ACACIA_WOOD = "stripped_acacia_wood"
    """Stripped Acacia Wood (ID: 158)"""

    STRIPPED_BAMBOO_BLOCK = "stripped_bamboo_block"
    """Block of Stripped Bamboo (ID: 164)"""

    STRIPPED_BIRCH_LOG = "stripped_birch_log"
    """Stripped Birch Log (ID: 146)"""

    STRIPPED_BIRCH_WOOD = "stripped_birch_wood"
    """Stripped Birch Wood (ID: 156)"""

    STRIPPED_CHERRY_LOG = "stripped_cherry_log"
    """Stripped Cherry Log (ID: 149)"""

    STRIPPED_CHERRY_WOOD = "stripped_cherry_wood"
    """Stripped Cherry Wood (ID: 159)"""

    STRIPPED_CRIMSON_HYPHAE = "stripped_crimson_hyphae"
    """Stripped Crimson Hyphae (ID: 162)"""

    STRIPPED_CRIMSON_STEM = "stripped_crimson_stem"
    """Stripped Crimson Stem (ID: 152)"""

    STRIPPED_DARK_OAK_LOG = "stripped_dark_oak_log"
    """Stripped Dark Oak Log (ID: 150)"""

    STRIPPED_DARK_OAK_WOOD = "stripped_dark_oak_wood"
    """Stripped Dark Oak Wood (ID: 160)"""

    STRIPPED_JUNGLE_LOG = "stripped_jungle_log"
    """Stripped Jungle Log (ID: 147)"""

    STRIPPED_JUNGLE_WOOD = "stripped_jungle_wood"
    """Stripped Jungle Wood (ID: 157)"""

    STRIPPED_MANGROVE_LOG = "stripped_mangrove_log"
    """Stripped Mangrove Log (ID: 151)"""

    STRIPPED_MANGROVE_WOOD = "stripped_mangrove_wood"
    """Stripped Mangrove Wood (ID: 161)"""

    STRIPPED_OAK_LOG = "stripped_oak_log"
    """Stripped Oak Log (ID: 144)"""

    STRIPPED_OAK_WOOD = "stripped_oak_wood"
    """Stripped Oak Wood (ID: 154)"""

    STRIPPED_SPRUCE_LOG = "stripped_spruce_log"
    """Stripped Spruce Log (ID: 145)"""

    STRIPPED_SPRUCE_WOOD = "stripped_spruce_wood"
    """Stripped Spruce Wood (ID: 155)"""

    STRIPPED_WARPED_HYPHAE = "stripped_warped_hyphae"
    """Stripped Warped Hyphae (ID: 163)"""

    STRIPPED_WARPED_STEM = "stripped_warped_stem"
    """Stripped Warped Stem (ID: 153)"""

    STRUCTURE_BLOCK = "structure_block"
    """Structure Block (ID: 791)"""

    STRUCTURE_VOID = "structure_void"
    """Structure Void (ID: 520)"""

    SUGAR = "sugar"
    """Sugar (ID: 959)"""

    SUGAR_CANE = "sugar_cane"
    """Sugar Cane (ID: 242)"""

    SUNFLOWER = "sunflower"
    """Sunflower (ID: 464)"""

    SUSPICIOUS_GRAVEL = "suspicious_gravel"
    """Suspicious Gravel (ID: 59)"""

    SUSPICIOUS_SAND = "suspicious_sand"
    """Suspicious Sand (ID: 58)"""

    SUSPICIOUS_STEW = "suspicious_stew"
    """Suspicious Stew (ID: 1183)"""

    SWEET_BERRIES = "sweet_berries"
    """Sweet Berries (ID: 1204)"""

    TADPOLE_BUCKET = "tadpole_bucket"
    """Bucket of Tadpole (ID: 917)"""

    TADPOLE_SPAWN_EGG = "tadpole_spawn_egg"
    """Tadpole Spawn Egg (ID: 1065)"""

    TALL_GRASS = "tall_grass"
    """Tall Grass (ID: 468)"""

    TARGET = "target"
    """Target (ID: 670)"""

    TERRACOTTA = "terracotta"
    """Terracotta (ID: 461)"""

    TIDE_ARMOR_TRIM_SMITHING_TEMPLATE = "tide_armor_trim_smithing_template"
    """Smithing Template (ID: 1265)"""

    TINTED_GLASS = "tinted_glass"
    """Tinted Glass (ID: 188)"""

    TIPPED_ARROW = "tipped_arrow"
    """Tipped Arrow (ID: 1153)"""

    TNT = "tnt"
    """TNT (ID: 678)"""

    TNT_MINECART = "tnt_minecart"
    """Minecart with TNT (ID: 768)"""

    TORCH = "torch"
    """Torch (ID: 290)"""

    TORCHFLOWER = "torchflower"
    """Torchflower (ID: 230)"""

    TORCHFLOWER_SEEDS = "torchflower_seeds"
    """Torchflower Seeds (ID: 1145)"""

    TOTEM_OF_UNDYING = "totem_of_undying"
    """Totem of Undying (ID: 1156)"""

    TRADER_LLAMA_SPAWN_EGG = "trader_llama_spawn_egg"
    """Trader Llama Spawn Egg (ID: 1066)"""

    TRAPPED_CHEST = "trapped_chest"
    """Trapped Chest (ID: 677)"""

    TRIAL_KEY = "trial_key"
    """Trial Key (ID: 1311)"""

    TRIAL_SPAWNER = "trial_spawner"
    """Trial Spawner (ID: 1310)"""

    TRIDENT = "trident"
    """Trident (ID: 1178)"""

    TRIPWIRE_HOOK = "tripwire_hook"
    """Tripwire Hook (ID: 676)"""

    TROPICAL_FISH = "tropical_fish"
    """Tropical Fish (ID: 934)"""

    TROPICAL_FISH_BUCKET = "tropical_fish_bucket"
    """Bucket of Tropical Fish (ID: 915)"""

    TROPICAL_FISH_SPAWN_EGG = "tropical_fish_spawn_egg"
    """Tropical Fish Spawn Egg (ID: 1067)"""

    TUBE_CORAL = "tube_coral"
    """Tube Coral (ID: 598)"""

    TUBE_CORAL_BLOCK = "tube_coral_block"
    """Tube Coral Block (ID: 593)"""

    TUBE_CORAL_FAN = "tube_coral_fan"
    """Tube Coral Fan (ID: 608)"""

    TUFF = "tuff"
    """Tuff (ID: 12)"""

    TUFF_BRICK_SLAB = "tuff_brick_slab"
    """Tuff Brick Slab (ID: 22)"""

    TUFF_BRICK_STAIRS = "tuff_brick_stairs"
    """Tuff Brick Stairs (ID: 23)"""

    TUFF_BRICK_WALL = "tuff_brick_wall"
    """Tuff Brick Wall (ID: 24)"""

    TUFF_BRICKS = "tuff_bricks"
    """Tuff Bricks (ID: 21)"""

    TUFF_SLAB = "tuff_slab"
    """Tuff Slab (ID: 13)"""

    TUFF_STAIRS = "tuff_stairs"
    """Tuff Stairs (ID: 14)"""

    TUFF_WALL = "tuff_wall"
    """Tuff Wall (ID: 15)"""

    TURTLE_EGG = "turtle_egg"
    """Turtle Egg (ID: 586)"""

    TURTLE_HELMET = "turtle_helmet"
    """Turtle Shell (ID: 793)"""

    TURTLE_SPAWN_EGG = "turtle_spawn_egg"
    """Turtle Spawn Egg (ID: 1068)"""

    TWISTING_VINES = "twisting_vines"
    """Twisting Vines (ID: 241)"""

    VERDANT_FROGLIGHT = "verdant_froglight"
    """Verdant Froglight (ID: 1252)"""

    VEX_ARMOR_TRIM_SMITHING_TEMPLATE = "vex_armor_trim_smithing_template"
    """Smithing Template (ID: 1264)"""

    VEX_SPAWN_EGG = "vex_spawn_egg"
    """Vex Spawn Egg (ID: 1069)"""

    VILLAGER_SPAWN_EGG = "villager_spawn_egg"
    """Villager Spawn Egg (ID: 1070)"""

    VINDICATOR_SPAWN_EGG = "vindicator_spawn_egg"
    """Vindicator Spawn Egg (ID: 1071)"""

    VINE = "vine"
    """Vines (ID: 358)"""

    WANDERING_TRADER_SPAWN_EGG = "wandering_trader_spawn_egg"
    """Wandering Trader Spawn Egg (ID: 1072)"""

    WARD_ARMOR_TRIM_SMITHING_TEMPLATE = "ward_armor_trim_smithing_template"
    """Smithing Template (ID: 1262)"""

    WARDEN_SPAWN_EGG = "warden_spawn_egg"
    """Warden Spawn Egg (ID: 1073)"""

    WARPED_BUTTON = "warped_button"
    """Warped Button (ID: 693)"""

    WARPED_DOOR = "warped_door"
    """Warped Door (ID: 720)"""

    WARPED_FENCE = "warped_fence"
    """Warped Fence (ID: 320)"""

    WARPED_FENCE_GATE = "warped_fence_gate"
    """Warped Fence Gate (ID: 759)"""

    WARPED_FUNGUS = "warped_fungus"
    """Warped Fungus (ID: 236)"""

    WARPED_FUNGUS_ON_A_STICK = "warped_fungus_on_a_stick"
    """Warped Fungus on a Stick (ID: 771)"""

    WARPED_HANGING_SIGN = "warped_hanging_sign"
    """Warped Hanging Sign (ID: 904)"""

    WARPED_HYPHAE = "warped_hyphae"
    """Warped Hyphae (ID: 174)"""

    WARPED_NYLIUM = "warped_nylium"
    """Warped Nylium (ID: 34)"""

    WARPED_PLANKS = "warped_planks"
    """Warped Planks (ID: 46)"""

    WARPED_PRESSURE_PLATE = "warped_pressure_plate"
    """Warped Pressure Plate (ID: 708)"""

    WARPED_ROOTS = "warped_roots"
    """Warped Roots (ID: 238)"""

    WARPED_SIGN = "warped_sign"
    """Warped Sign (ID: 893)"""

    WARPED_SLAB = "warped_slab"
    """Warped Slab (ID: 262)"""

    WARPED_STAIRS = "warped_stairs"
    """Warped Stairs (ID: 393)"""

    WARPED_STEM = "warped_stem"
    """Warped Stem (ID: 142)"""

    WARPED_TRAPDOOR = "warped_trapdoor"
    """Warped Trapdoor (ID: 740)"""

    WARPED_WART_BLOCK = "warped_wart_block"
    """Warped Wart Block (ID: 517)"""

    WATER_BUCKET = "water_bucket"
    """Water Bucket (ID: 906)"""

    WAXED_CHISELED_COPPER = "waxed_chiseled_copper"
    """Waxed Chiseled Copper (ID: 115)"""

    WAXED_COPPER_BLOCK = "waxed_copper_block"
    """Waxed Block of Copper (ID: 111)"""

    WAXED_COPPER_BULB = "waxed_copper_bulb"
    """Waxed Copper Bulb (ID: 1306)"""

    WAXED_COPPER_DOOR = "waxed_copper_door"
    """Waxed Copper Door (ID: 725)"""

    WAXED_COPPER_GRATE = "waxed_copper_grate"
    """Waxed Copper Grate (ID: 1298)"""

    WAXED_COPPER_TRAPDOOR = "waxed_copper_trapdoor"
    """Waxed Copper Trapdoor (ID: 745)"""

    WAXED_CUT_COPPER = "waxed_cut_copper"
    """Waxed Cut Copper (ID: 119)"""

    WAXED_CUT_COPPER_SLAB = "waxed_cut_copper_slab"
    """Waxed Cut Copper Slab (ID: 127)"""

    WAXED_CUT_COPPER_STAIRS = "waxed_cut_copper_stairs"
    """Waxed Cut Copper Stairs (ID: 123)"""

    WAXED_EXPOSED_CHISELED_COPPER = "waxed_exposed_chiseled_copper"
    """Waxed Exposed Chiseled Copper (ID: 116)"""

    WAXED_EXPOSED_COPPER = "waxed_exposed_copper"
    """Waxed Exposed Copper (ID: 112)"""

    WAXED_EXPOSED_COPPER_BULB = "waxed_exposed_copper_bulb"
    """Waxed Exposed Copper Bulb (ID: 1307)"""

    WAXED_EXPOSED_COPPER_DOOR = "waxed_exposed_copper_door"
    """Waxed Exposed Copper Door (ID: 726)"""

    WAXED_EXPOSED_COPPER_GRATE = "waxed_exposed_copper_grate"
    """Waxed Exposed Copper Grate (ID: 1299)"""

    WAXED_EXPOSED_COPPER_TRAPDOOR = "waxed_exposed_copper_trapdoor"
    """Waxed Exposed Copper Trapdoor (ID: 746)"""

    WAXED_EXPOSED_CUT_COPPER = "waxed_exposed_cut_copper"
    """Waxed Exposed Cut Copper (ID: 120)"""

    WAXED_EXPOSED_CUT_COPPER_SLAB = "waxed_exposed_cut_copper_slab"
    """Waxed Exposed Cut Copper Slab (ID: 128)"""

    WAXED_EXPOSED_CUT_COPPER_STAIRS = "waxed_exposed_cut_copper_stairs"
    """Waxed Exposed Cut Copper Stairs (ID: 124)"""

    WAXED_OXIDIZED_CHISELED_COPPER = "waxed_oxidized_chiseled_copper"
    """Waxed Oxidized Chiseled Copper (ID: 118)"""

    WAXED_OXIDIZED_COPPER = "waxed_oxidized_copper"
    """Waxed Oxidized Copper (ID: 114)"""

    WAXED_OXIDIZED_COPPER_BULB = "waxed_oxidized_copper_bulb"
    """Waxed Oxidized Copper Bulb (ID: 1309)"""

    WAXED_OXIDIZED_COPPER_DOOR = "waxed_oxidized_copper_door"
    """Waxed Oxidized Copper Door (ID: 728)"""

    WAXED_OXIDIZED_COPPER_GRATE = "waxed_oxidized_copper_grate"
    """Waxed Oxidized Copper Grate (ID: 1301)"""

    WAXED_OXIDIZED_COPPER_TRAPDOOR = "waxed_oxidized_copper_trapdoor"
    """Waxed Oxidized Copper Trapdoor (ID: 748)"""

    WAXED_OXIDIZED_CUT_COPPER = "waxed_oxidized_cut_copper"
    """Waxed Oxidized Cut Copper (ID: 122)"""

    WAXED_OXIDIZED_CUT_COPPER_SLAB = "waxed_oxidized_cut_copper_slab"
    """Waxed Oxidized Cut Copper Slab (ID: 130)"""

    WAXED_OXIDIZED_CUT_COPPER_STAIRS = "waxed_oxidized_cut_copper_stairs"
    """Waxed Oxidized Cut Copper Stairs (ID: 126)"""

    WAXED_WEATHERED_CHISELED_COPPER = "waxed_weathered_chiseled_copper"
    """Waxed Weathered Chiseled Copper (ID: 117)"""

    WAXED_WEATHERED_COPPER = "waxed_weathered_copper"
    """Waxed Weathered Copper (ID: 113)"""

    WAXED_WEATHERED_COPPER_BULB = "waxed_weathered_copper_bulb"
    """Waxed Weathered Copper Bulb (ID: 1308)"""

    WAXED_WEATHERED_COPPER_DOOR = "waxed_weathered_copper_door"
    """Waxed Weathered Copper Door (ID: 727)"""

    WAXED_WEATHERED_COPPER_GRATE = "waxed_weathered_copper_grate"
    """Waxed Weathered Copper Grate (ID: 1300)"""

    WAXED_WEATHERED_COPPER_TRAPDOOR = "waxed_weathered_copper_trapdoor"
    """Waxed Weathered Copper Trapdoor (ID: 747)"""

    WAXED_WEATHERED_CUT_COPPER = "waxed_weathered_cut_copper"
    """Waxed Weathered Cut Copper (ID: 121)"""

    WAXED_WEATHERED_CUT_COPPER_SLAB = "waxed_weathered_cut_copper_slab"
    """Waxed Weathered Cut Copper Slab (ID: 129)"""

    WAXED_WEATHERED_CUT_COPPER_STAIRS = "waxed_weathered_cut_copper_stairs"
    """Waxed Weathered Cut Copper Stairs (ID: 125)"""

    WAYFINDER_ARMOR_TRIM_SMITHING_TEMPLATE = "wayfinder_armor_trim_smithing_template"
    """Smithing Template (ID: 1269)"""

    WEATHERED_CHISELED_COPPER = "weathered_chiseled_copper"
    """Weathered Chiseled Copper (ID: 97)"""

    WEATHERED_COPPER = "weathered_copper"
    """Weathered Copper (ID: 93)"""

    WEATHERED_COPPER_BULB = "weathered_copper_bulb"
    """Weathered Copper Bulb (ID: 1304)"""

    WEATHERED_COPPER_DOOR = "weathered_copper_door"
    """Weathered Copper Door (ID: 723)"""

    WEATHERED_COPPER_GRATE = "weathered_copper_grate"
    """Weathered Copper Grate (ID: 1296)"""

    WEATHERED_COPPER_TRAPDOOR = "weathered_copper_trapdoor"
    """Weathered Copper Trapdoor (ID: 743)"""

    WEATHERED_CUT_COPPER = "weathered_cut_copper"
    """Weathered Cut Copper (ID: 101)"""

    WEATHERED_CUT_COPPER_SLAB = "weathered_cut_copper_slab"
    """Weathered Cut Copper Slab (ID: 109)"""

    WEATHERED_CUT_COPPER_STAIRS = "weathered_cut_copper_stairs"
    """Weathered Cut Copper Stairs (ID: 105)"""

    WEEPING_VINES = "weeping_vines"
    """Weeping Vines (ID: 240)"""

    WET_SPONGE = "wet_sponge"
    """Wet Sponge (ID: 186)"""

    WHEAT = "wheat"
    """Wheat (ID: 851)"""

    WHEAT_SEEDS = "wheat_seeds"
    """Wheat Seeds (ID: 850)"""

    WHITE_BANNER = "white_banner"
    """White Banner (ID: 1126)"""

    WHITE_BED = "white_bed"
    """White Bed (ID: 961)"""

    WHITE_CANDLE = "white_candle"
    """White Candle (ID: 1230)"""

    WHITE_CARPET = "white_carpet"
    """White Carpet (ID: 445)"""

    WHITE_CONCRETE = "white_concrete"
    """White Concrete (ID: 554)"""

    WHITE_CONCRETE_POWDER = "white_concrete_powder"
    """White Concrete Powder (ID: 570)"""

    WHITE_DYE = "white_dye"
    """White Dye (ID: 941)"""

    WHITE_GLAZED_TERRACOTTA = "white_glazed_terracotta"
    """White Glazed Terracotta (ID: 538)"""

    WHITE_SHULKER_BOX = "white_shulker_box"
    """White Shulker Box (ID: 522)"""

    WHITE_STAINED_GLASS = "white_stained_glass"
    """White Stained Glass (ID: 470)"""

    WHITE_STAINED_GLASS_PANE = "white_stained_glass_pane"
    """White Stained Glass Pane (ID: 486)"""

    WHITE_TERRACOTTA = "white_terracotta"
    """White Terracotta (ID: 426)"""

    WHITE_TULIP = "white_tulip"
    """White Tulip (ID: 224)"""

    WHITE_WOOL = "white_wool"
    """White Wool (ID: 201)"""

    WILD_ARMOR_TRIM_SMITHING_TEMPLATE = "wild_armor_trim_smithing_template"
    """Smithing Template (ID: 1261)"""

    WITCH_SPAWN_EGG = "witch_spawn_egg"
    """Witch Spawn Egg (ID: 1074)"""

    WITHER_ROSE = "wither_rose"
    """Wither Rose (ID: 229)"""

    WITHER_SKELETON_SKULL = "wither_skeleton_skull"
    """Wither Skeleton Skull (ID: 1097)"""

    WITHER_SKELETON_SPAWN_EGG = "wither_skeleton_spawn_egg"
    """Wither Skeleton Spawn Egg (ID: 1076)"""

    WITHER_SPAWN_EGG = "wither_spawn_egg"
    """Wither Spawn Egg (ID: 1075)"""

    WOLF_SPAWN_EGG = "wolf_spawn_egg"
    """Wolf Spawn Egg (ID: 1077)"""

    WOODEN_AXE = "wooden_axe"
    """Wooden Axe (ID: 817)"""

    WOODEN_HOE = "wooden_hoe"
    """Wooden Hoe (ID: 818)"""

    WOODEN_PICKAXE = "wooden_pickaxe"
    """Wooden Pickaxe (ID: 816)"""

    WOODEN_SHOVEL = "wooden_shovel"
    """Wooden Shovel (ID: 815)"""

    WOODEN_SWORD = "wooden_sword"
    """Wooden Sword (ID: 814)"""

    WRITABLE_BOOK = "writable_book"
    """Book and Quill (ID: 1085)"""

    WRITTEN_BOOK = "written_book"
    """Written Book (ID: 1086)"""

    YELLOW_BANNER = "yellow_banner"
    """Yellow Banner (ID: 1130)"""

    YELLOW_BED = "yellow_bed"
    """Yellow Bed (ID: 965)"""

    YELLOW_CANDLE = "yellow_candle"
    """Yellow Candle (ID: 1234)"""

    YELLOW_CARPET = "yellow_carpet"
    """Yellow Carpet (ID: 449)"""

    YELLOW_CONCRETE = "yellow_concrete"
    """Yellow Concrete (ID: 558)"""

    YELLOW_CONCRETE_POWDER = "yellow_concrete_powder"
    """Yellow Concrete Powder (ID: 574)"""

    YELLOW_DYE = "yellow_dye"
    """Yellow Dye (ID: 945)"""

    YELLOW_GLAZED_TERRACOTTA = "yellow_glazed_terracotta"
    """Yellow Glazed Terracotta (ID: 542)"""

    YELLOW_SHULKER_BOX = "yellow_shulker_box"
    """Yellow Shulker Box (ID: 526)"""

    YELLOW_STAINED_GLASS = "yellow_stained_glass"
    """Yellow Stained Glass (ID: 474)"""

    YELLOW_STAINED_GLASS_PANE = "yellow_stained_glass_pane"
    """Yellow Stained Glass Pane (ID: 490)"""

    YELLOW_TERRACOTTA = "yellow_terracotta"
    """Yellow Terracotta (ID: 430)"""

    YELLOW_WOOL = "yellow_wool"
    """Yellow Wool (ID: 205)"""

    ZOGLIN_SPAWN_EGG = "zoglin_spawn_egg"
    """Zoglin Spawn Egg (ID: 1078)"""

    ZOMBIE_HEAD = "zombie_head"
    """Zombie Head (ID: 1099)"""

    ZOMBIE_HORSE_SPAWN_EGG = "zombie_horse_spawn_egg"
    """Zombie Horse Spawn Egg (ID: 1080)"""

    ZOMBIE_SPAWN_EGG = "zombie_spawn_egg"
    """Zombie Spawn Egg (ID: 1079)"""

    ZOMBIE_VILLAGER_SPAWN_EGG = "zombie_villager_spawn_egg"
    """Zombie Villager Spawn Egg (ID: 1081)"""

    ZOMBIFIED_PIGLIN_SPAWN_EGG = "zombified_piglin_spawn_egg"
    """Zombified Piglin Spawn Egg (ID: 1082)"""


class MCEntities(MCEnum):
    """Entity types representing all spawnable entities in Minecraft.

    All values are sourced from minecraft-data and match the game's internal identifiers.
    """

    ALLAY = "allay"
    """Allay (ID: 0)"""

    AREA_EFFECT_CLOUD = "area_effect_cloud"
    """Area Effect Cloud (ID: 1)"""

    ARMOR_STAND = "armor_stand"
    """Armor Stand (ID: 2)"""

    ARROW = "arrow"
    """Arrow (ID: 3)"""

    AXOLOTL = "axolotl"
    """Axolotl (ID: 4)"""

    BAT = "bat"
    """Bat (ID: 5)"""

    BEE = "bee"
    """Bee (ID: 6)"""

    BLAZE = "blaze"
    """Blaze (ID: 7)"""

    BLOCK_DISPLAY = "block_display"
    """Block Display (ID: 8)"""

    BOAT = "boat"
    """Boat (ID: 9)"""

    BREEZE = "breeze"
    """Breeze (ID: 10)"""

    CAMEL = "camel"
    """Camel (ID: 11)"""

    CAT = "cat"
    """Cat (ID: 12)"""

    CAVE_SPIDER = "cave_spider"
    """Cave Spider (ID: 13)"""

    CHEST_BOAT = "chest_boat"
    """Boat with Chest (ID: 14)"""

    CHEST_MINECART = "chest_minecart"
    """Minecart with Chest (ID: 15)"""

    CHICKEN = "chicken"
    """Chicken (ID: 16)"""

    COD = "cod"
    """Cod (ID: 17)"""

    COMMAND_BLOCK_MINECART = "command_block_minecart"
    """Minecart with Command Block (ID: 18)"""

    COW = "cow"
    """Cow (ID: 19)"""

    CREEPER = "creeper"
    """Creeper (ID: 20)"""

    DOLPHIN = "dolphin"
    """Dolphin (ID: 21)"""

    DONKEY = "donkey"
    """Donkey (ID: 22)"""

    DRAGON_FIREBALL = "dragon_fireball"
    """Dragon Fireball (ID: 23)"""

    DROWNED = "drowned"
    """Drowned (ID: 24)"""

    EGG = "egg"
    """Thrown Egg (ID: 25)"""

    ELDER_GUARDIAN = "elder_guardian"
    """Elder Guardian (ID: 26)"""

    END_CRYSTAL = "end_crystal"
    """End Crystal (ID: 27)"""

    ENDER_DRAGON = "ender_dragon"
    """Ender Dragon (ID: 28)"""

    ENDER_PEARL = "ender_pearl"
    """Thrown Ender Pearl (ID: 29)"""

    ENDERMAN = "enderman"
    """Enderman (ID: 30)"""

    ENDERMITE = "endermite"
    """Endermite (ID: 31)"""

    EVOKER = "evoker"
    """Evoker (ID: 32)"""

    EVOKER_FANGS = "evoker_fangs"
    """Evoker Fangs (ID: 33)"""

    EXPERIENCE_BOTTLE = "experience_bottle"
    """Thrown Bottle o' Enchanting (ID: 34)"""

    EXPERIENCE_ORB = "experience_orb"
    """Experience Orb (ID: 35)"""

    EYE_OF_ENDER = "eye_of_ender"
    """Eye of Ender (ID: 36)"""

    FALLING_BLOCK = "falling_block"
    """Falling Block (ID: 37)"""

    FIREBALL = "fireball"
    """Fireball (ID: 58)"""

    FIREWORK_ROCKET = "firework_rocket"
    """Firework Rocket (ID: 38)"""

    FISHING_BOBBER = "fishing_bobber"
    """Fishing Bobber (ID: 125)"""

    FOX = "fox"
    """Fox (ID: 39)"""

    FROG = "frog"
    """Frog (ID: 40)"""

    FURNACE_MINECART = "furnace_minecart"
    """Minecart with Furnace (ID: 41)"""

    GHAST = "ghast"
    """Ghast (ID: 42)"""

    GIANT = "giant"
    """Giant (ID: 43)"""

    GLOW_ITEM_FRAME = "glow_item_frame"
    """Glow Item Frame (ID: 44)"""

    GLOW_SQUID = "glow_squid"
    """Glow Squid (ID: 45)"""

    GOAT = "goat"
    """Goat (ID: 46)"""

    GUARDIAN = "guardian"
    """Guardian (ID: 47)"""

    HOGLIN = "hoglin"
    """Hoglin (ID: 48)"""

    HOPPER_MINECART = "hopper_minecart"
    """Minecart with Hopper (ID: 49)"""

    HORSE = "horse"
    """Horse (ID: 50)"""

    HUSK = "husk"
    """Husk (ID: 51)"""

    ILLUSIONER = "illusioner"
    """Illusioner (ID: 52)"""

    INTERACTION = "interaction"
    """Interaction (ID: 53)"""

    IRON_GOLEM = "iron_golem"
    """Iron Golem (ID: 54)"""

    ITEM = "item"
    """Item (ID: 55)"""

    ITEM_DISPLAY = "item_display"
    """Item Display (ID: 56)"""

    ITEM_FRAME = "item_frame"
    """Item Frame (ID: 57)"""

    LEASH_KNOT = "leash_knot"
    """Leash Knot (ID: 59)"""

    LIGHTNING_BOLT = "lightning_bolt"
    """Lightning Bolt (ID: 60)"""

    LLAMA = "llama"
    """Llama (ID: 61)"""

    LLAMA_SPIT = "llama_spit"
    """Llama Spit (ID: 62)"""

    MAGMA_CUBE = "magma_cube"
    """Magma Cube (ID: 63)"""

    MARKER = "marker"
    """Marker (ID: 64)"""

    MINECART = "minecart"
    """Minecart (ID: 65)"""

    MOOSHROOM = "mooshroom"
    """Mooshroom (ID: 66)"""

    MULE = "mule"
    """Mule (ID: 67)"""

    OCELOT = "ocelot"
    """Ocelot (ID: 68)"""

    PAINTING = "painting"
    """Painting (ID: 69)"""

    PANDA = "panda"
    """Panda (ID: 70)"""

    PARROT = "parrot"
    """Parrot (ID: 71)"""

    PHANTOM = "phantom"
    """Phantom (ID: 72)"""

    PIG = "pig"
    """Pig (ID: 73)"""

    PIGLIN = "piglin"
    """Piglin (ID: 74)"""

    PIGLIN_BRUTE = "piglin_brute"
    """Piglin Brute (ID: 75)"""

    PILLAGER = "pillager"
    """Pillager (ID: 76)"""

    PLAYER = "player"
    """Player (ID: 124)"""

    POLAR_BEAR = "polar_bear"
    """Polar Bear (ID: 77)"""

    POTION = "potion"
    """Potion (ID: 78)"""

    PUFFERFISH = "pufferfish"
    """Pufferfish (ID: 79)"""

    RABBIT = "rabbit"
    """Rabbit (ID: 80)"""

    RAVAGER = "ravager"
    """Ravager (ID: 81)"""

    SALMON = "salmon"
    """Salmon (ID: 82)"""

    SHEEP = "sheep"
    """Sheep (ID: 83)"""

    SHULKER = "shulker"
    """Shulker (ID: 84)"""

    SHULKER_BULLET = "shulker_bullet"
    """Shulker Bullet (ID: 85)"""

    SILVERFISH = "silverfish"
    """Silverfish (ID: 86)"""

    SKELETON = "skeleton"
    """Skeleton (ID: 87)"""

    SKELETON_HORSE = "skeleton_horse"
    """Skeleton Horse (ID: 88)"""

    SLIME = "slime"
    """Slime (ID: 89)"""

    SMALL_FIREBALL = "small_fireball"
    """Small Fireball (ID: 90)"""

    SNIFFER = "sniffer"
    """Sniffer (ID: 91)"""

    SNOW_GOLEM = "snow_golem"
    """Snow Golem (ID: 92)"""

    SNOWBALL = "snowball"
    """Snowball (ID: 93)"""

    SPAWNER_MINECART = "spawner_minecart"
    """Minecart with Monster Spawner (ID: 94)"""

    SPECTRAL_ARROW = "spectral_arrow"
    """Spectral Arrow (ID: 95)"""

    SPIDER = "spider"
    """Spider (ID: 96)"""

    SQUID = "squid"
    """Squid (ID: 97)"""

    STRAY = "stray"
    """Stray (ID: 98)"""

    STRIDER = "strider"
    """Strider (ID: 99)"""

    TADPOLE = "tadpole"
    """Tadpole (ID: 100)"""

    TEXT_DISPLAY = "text_display"
    """Text Display (ID: 101)"""

    TNT = "tnt"
    """Primed TNT (ID: 102)"""

    TNT_MINECART = "tnt_minecart"
    """Minecart with TNT (ID: 103)"""

    TRADER_LLAMA = "trader_llama"
    """Trader Llama (ID: 104)"""

    TRIDENT = "trident"
    """Trident (ID: 105)"""

    TROPICAL_FISH = "tropical_fish"
    """Tropical Fish (ID: 106)"""

    TURTLE = "turtle"
    """Turtle (ID: 107)"""

    VEX = "vex"
    """Vex (ID: 108)"""

    VILLAGER = "villager"
    """Villager (ID: 109)"""

    VINDICATOR = "vindicator"
    """Vindicator (ID: 110)"""

    WANDERING_TRADER = "wandering_trader"
    """Wandering Trader (ID: 111)"""

    WARDEN = "warden"
    """Warden (ID: 112)"""

    WIND_CHARGE = "wind_charge"
    """Wind Charge (ID: 113)"""

    WITCH = "witch"
    """Witch (ID: 114)"""

    WITHER = "wither"
    """Wither (ID: 115)"""

    WITHER_SKELETON = "wither_skeleton"
    """Wither Skeleton (ID: 116)"""

    WITHER_SKULL = "wither_skull"
    """Wither Skull (ID: 117)"""

    WOLF = "wolf"
    """Wolf (ID: 118)"""

    ZOGLIN = "zoglin"
    """Zoglin (ID: 119)"""

    ZOMBIE = "zombie"
    """Zombie (ID: 120)"""

    ZOMBIE_HORSE = "zombie_horse"
    """Zombie Horse (ID: 121)"""

    ZOMBIE_VILLAGER = "zombie_villager"
    """Zombie Villager (ID: 122)"""

    ZOMBIFIED_PIGLIN = "zombified_piglin"
    """Zombified Piglin (ID: 123)"""


class MCBiomes(MCEnum):
    """Biome types representing all possible world biomes in Minecraft.

    All values are sourced from minecraft-data and match the game's internal identifiers.
    """

    BADLANDS = "badlands"
    """Badlands (ID: 0)"""

    BAMBOO_JUNGLE = "bamboo_jungle"
    """Bamboo Jungle (ID: 1)"""

    BASALT_DELTAS = "basalt_deltas"
    """Basalt Deltas (ID: 2)"""

    BEACH = "beach"
    """Beach (ID: 3)"""

    BIRCH_FOREST = "birch_forest"
    """Birch Forest (ID: 4)"""

    CHERRY_GROVE = "cherry_grove"
    """Cherry Grove (ID: 5)"""

    COLD_OCEAN = "cold_ocean"
    """Cold Ocean (ID: 6)"""

    CRIMSON_FOREST = "crimson_forest"
    """Crimson Forest (ID: 7)"""

    DARK_FOREST = "dark_forest"
    """Dark Forest (ID: 8)"""

    DEEP_COLD_OCEAN = "deep_cold_ocean"
    """Deep Cold Ocean (ID: 9)"""

    DEEP_DARK = "deep_dark"
    """Deep Dark (ID: 10)"""

    DEEP_FROZEN_OCEAN = "deep_frozen_ocean"
    """Deep Frozen Ocean (ID: 11)"""

    DEEP_LUKEWARM_OCEAN = "deep_lukewarm_ocean"
    """Deep Lukewarm Ocean (ID: 12)"""

    DEEP_OCEAN = "deep_ocean"
    """Deep Ocean (ID: 13)"""

    DESERT = "desert"
    """Desert (ID: 14)"""

    DRIPSTONE_CAVES = "dripstone_caves"
    """Dripstone Caves (ID: 15)"""

    END_BARRENS = "end_barrens"
    """End Barrens (ID: 16)"""

    END_HIGHLANDS = "end_highlands"
    """End Highlands (ID: 17)"""

    END_MIDLANDS = "end_midlands"
    """End Midlands (ID: 18)"""

    ERODED_BADLANDS = "eroded_badlands"
    """Eroded Badlands (ID: 19)"""

    FLOWER_FOREST = "flower_forest"
    """Flower Forest (ID: 20)"""

    FOREST = "forest"
    """Forest (ID: 21)"""

    FROZEN_OCEAN = "frozen_ocean"
    """Frozen Ocean (ID: 22)"""

    FROZEN_PEAKS = "frozen_peaks"
    """Frozen Peaks (ID: 23)"""

    FROZEN_RIVER = "frozen_river"
    """Frozen River (ID: 24)"""

    GROVE = "grove"
    """Grove (ID: 25)"""

    ICE_SPIKES = "ice_spikes"
    """Ice Spikes (ID: 26)"""

    JAGGED_PEAKS = "jagged_peaks"
    """Jagged Peaks (ID: 27)"""

    JUNGLE = "jungle"
    """Jungle (ID: 28)"""

    LUKEWARM_OCEAN = "lukewarm_ocean"
    """Lukewarm Ocean (ID: 29)"""

    LUSH_CAVES = "lush_caves"
    """Lush Caves (ID: 30)"""

    MANGROVE_SWAMP = "mangrove_swamp"
    """Mangrove Swamp (ID: 31)"""

    MEADOW = "meadow"
    """Meadow (ID: 32)"""

    MUSHROOM_FIELDS = "mushroom_fields"
    """Mushroom Fields (ID: 33)"""

    NETHER_WASTES = "nether_wastes"
    """Nether Wastes (ID: 34)"""

    OCEAN = "ocean"
    """Ocean (ID: 35)"""

    OLD_GROWTH_BIRCH_FOREST = "old_growth_birch_forest"
    """Old Growth Birch Forest (ID: 36)"""

    OLD_GROWTH_PINE_TAIGA = "old_growth_pine_taiga"
    """Old Growth Pine Taiga (ID: 37)"""

    OLD_GROWTH_SPRUCE_TAIGA = "old_growth_spruce_taiga"
    """Old Growth Spruce Taiga (ID: 38)"""

    PLAINS = "plains"
    """Plains (ID: 39)"""

    RIVER = "river"
    """River (ID: 40)"""

    SAVANNA = "savanna"
    """Savanna (ID: 41)"""

    SAVANNA_PLATEAU = "savanna_plateau"
    """Savanna Plateau (ID: 42)"""

    SMALL_END_ISLANDS = "small_end_islands"
    """Small End Islands (ID: 43)"""

    SNOWY_BEACH = "snowy_beach"
    """Snowy Beach (ID: 44)"""

    SNOWY_PLAINS = "snowy_plains"
    """Snowy Plains (ID: 45)"""

    SNOWY_SLOPES = "snowy_slopes"
    """Snowy Slopes (ID: 46)"""

    SNOWY_TAIGA = "snowy_taiga"
    """Snowy Taiga (ID: 47)"""

    SOUL_SAND_VALLEY = "soul_sand_valley"
    """Soul Sand Valley (ID: 48)"""

    SPARSE_JUNGLE = "sparse_jungle"
    """Sparse Jungle (ID: 49)"""

    STONY_PEAKS = "stony_peaks"
    """Stony Peaks (ID: 50)"""

    STONY_SHORE = "stony_shore"
    """Stony Shore (ID: 51)"""

    SUNFLOWER_PLAINS = "sunflower_plains"
    """Sunflower Plains (ID: 52)"""

    SWAMP = "swamp"
    """Swamp (ID: 53)"""

    TAIGA = "taiga"
    """Taiga (ID: 54)"""

    THE_END = "the_end"
    """The End (ID: 55)"""

    THE_VOID = "the_void"
    """The Void (ID: 56)"""

    WARM_OCEAN = "warm_ocean"
    """Warm Ocean (ID: 57)"""

    WARPED_FOREST = "warped_forest"
    """Warped Forest (ID: 58)"""

    WINDSWEPT_FOREST = "windswept_forest"
    """Windswept Forest (ID: 59)"""

    WINDSWEPT_GRAVELLY_HILLS = "windswept_gravelly_hills"
    """Windswept Gravelly Hills (ID: 60)"""

    WINDSWEPT_HILLS = "windswept_hills"
    """Windswept Hills (ID: 61)"""

    WINDSWEPT_SAVANNA = "windswept_savanna"
    """Windswept Savanna (ID: 62)"""

    WOODED_BADLANDS = "wooded_badlands"
    """Wooded Badlands (ID: 63)"""


class MC:
    """
    Static access to Minecraft game elements from minecraft-data 1.20.4.

    Attributes:
        blocks: All block types in the game. Each value represents a unique
            block and can be used anywhere a block identifier is needed.
            Example: MC.blocks.STONE

        items: All item types in the game. Each value represents a unique
            item and can be used anywhere an item identifier is needed.
            Example: MC.items.DIAMOND

        entities: All entity types in the game. Each value represents a unique
            entity and can be used anywhere an entity identifier is needed.
            Example: MC.entities.ZOMBIE

        biomes: All biome types in the game. Each value represents a unique
            biome and can be used anywhere a biome identifier is needed.
            Example: MC.biomes.PLAINS
    """

    blocks: Final[type[MCBlocks]] = MCBlocks
    items: Final[type[MCItems]] = MCItems
    entities: Final[type[MCEntities]] = MCEntities
    biomes: Final[type[MCBiomes]] = MCBiomes
