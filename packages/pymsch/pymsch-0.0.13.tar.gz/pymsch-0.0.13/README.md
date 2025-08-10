 # pymsch

 a package for generating mindustry schematic files with python code

 here's a basic example:
 ```py
 from pymsch import Schematic, Block, Content

 schem = Schematic()
 schem.set_tag('name', 'Example Schematic')
 schem.set_tag('description', 'A description for the schematic')

 schem.add_block(Block(Content.COPPER_WALL, 0, 0, None, 0))

 schem.write_clipboard()
 ```
 This makes a schematic with a single copper wall, and outputs it to your clipboard to import into the game

 