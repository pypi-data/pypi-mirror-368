#!/usr/bin/env python3

from fire import Fire
from console import fg,bg
BEST = f"""
{fg.yellow}# TOOLS: u {fg.default}
cmd_ai  "Pocasi zitra ve Stredoceskem kraji: jaka bude nejvyssi teplota?" -u
cmd_ai  "Pocasi zitra ve Stredoceskem kraji, ne na zapade, jihu, severu, vychode: bude prset?" -u
cmd_ai  "Pocasi zitra ve Stredoceskem kraji, ne na zapade, jihu, severu, vychode: bude prset? Velmi strucne!" -u --csspeak

cmd_ai "From the site https://www.zakruta.cz/dopravni-informace-nehody/ - extract the current accidents and list those in Prague"

{fg.yellow}# COMMIT commads{fg.default}
git diff | cmd_ai "Create oneliner git commit command with -a -m parameters "

{fg.yellow}# Tricking AI{fg.default}
Muz a ovce jsou na jedne strane reky, kde stoji clun. Jaky je postup, aby muz i ovce nakonec byli na druhe strane reky?
Pepa ma 3 bratry a 4 sestry, jedna z nich je Ema. Kolik ma Ema bratru?
Z Brna do Prahy je to 150km. Vlak z Prahy do Brna jede rychlosti 100km/h. Vlak z Brna do Prahy jede rychlosti 50km/h. Za jak dlouho se vlaky potkaji, pokud je ridi ten samy strojvudce?
Kráčíte ke dveřím rychlostí 1km/h a jste 10 metrů od dveří. S každým pohybem směrem k nim snížíte vzdálenost o polovinu, kdy se dostanete ke dveřím?

{fg.yellow}CMDLINE:{fg.default}
-a vision  "opcam_20240601_181417.jpg Je to penizovka? Ma tenky stonek a tenky klobouk."

"""
def main():
    print(BEST)

if __name__=="__main__":
    Fire(main)
