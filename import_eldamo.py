"""
import_eldamo.py  (v2)
─────────────────────
Extrai palavras Sindarin do eldamo-data.xml e mescla com o léxico
PT existente, gerando um pt-sindarin.json mais completo e confiável.

Estratégias de mapeamento de gloss → PT:
1. Match direto com dicionário EN→PT
2. Split por vírgula/ponto e vírgula → tenta cada parte
3. Para glosses compostos (ex: "great river"), tenta as palavras individuais
4. Filtra nomes próprios, sufixos e entradas sem tradução

Uso:  python import_eldamo.py
"""

import json
import xml.etree.ElementTree as ET
import re
from collections import Counter
from typing import cast

# ─── Dicionário EN → PT (expansivo) ──────────────────────────────────────────
EN_PT = {
    # Artigos/pronomes
    "the": "o", "a": "um", "he": "ele", "she": "ela",
    "it": "isso", "they": "eles", "we": "nós",
    "i": "eu", "you": "tu", "me": "me",
    "his": "seu", "her": "sua", "their": "deles", "our": "nosso",
    "my": "meu", "thy": "teu", "who": "quem", "which": "que",
    # Preposições/conjunções
    "and": "e", "but": "mas", "or": "ou", "if": "se",
    "because": "porque", "from": "de", "of": "de", "in": "em",
    "to": "para", "with": "com", "without": "sem",
    "under": "sob", "above": "sobre", "between": "entre",
    "before": "antes", "after": "depois", "at": "em",
    "on": "em", "for": "por", "by": "por",
    "through": "através", "beyond": "além", "against": "contra",
    "not": "não", "no": "não", "yes": "sim",
    "now": "agora", "here": "aqui", "there": "ali",
    "always": "sempre", "never": "nunca", "only": "apenas",
    "also": "também", "yet": "ainda", "then": "então",
    "very": "muito", "more": "mais", "less": "menos",
    # Natureza — água
    "water": "água", "waters": "águas",
    "river": "rio", "rivers": "rios",
    "sea": "mar", "ocean": "oceano",
    "lake": "lago", "pool": "lago", "mere": "lago",
    "marsh": "pântano", "fen": "pântano", "bog": "pântano",
    "spring": "nascente", "source": "fonte", "well": "poço",
    "stream": "córrego", "brook": "riacho",
    "waterfall": "cachoeira", "fall": "cachoeira",
    "flood": "enchente", "fountain": "fonte",
    "bay": "baía", "gulf": "golfo",
    # Natureza — terra
    "land": "terra", "earth": "terra", "soil": "solo",
    "ground": "chão", "floor": "chão", "floor": "chão",
    "world": "mundo", "middle-earth": "terra-média",
    "country": "país", "region": "região", "realm": "reino",
    "shore": "praia", "coast": "costa", "beach": "praia",
    "island": "ilha", "isle": "ilha", "peninsula": "península",
    "mountain": "montanha", "mountains": "montanhas",
    "peak": "pico", "summit": "cume", "top": "topo",
    "hill": "colina", "hills": "colinas", "mound": "outeiro",
    "valley": "vale", "dale": "vale", "hollow": "depressão",
    "plain": "planície", "field": "campo", "mead": "prado",
    "meadow": "prado", "downs": "colinas",
    "desert": "deserto", "waste": "ermo",
    "cliff": "penhasco", "ravine": "ravina",
    "gorge": "desfiladeiro", "pass": "desfiladeiro", "gap": "abertura",
    "cave": "caverna", "grotto": "caverna", "hole": "buraco",
    "mine": "mina", "pit": "poço",
    "gate": "portão", "door": "porta",
    "bridge": "ponte", "ford": "vau",
    "path": "caminho", "track": "trilha",
    "road": "estrada", "way": "caminho",
    "passage": "passagem", "course": "curso",
    "forest": "floresta", "wood": "bosque", "woods": "bosque",
    "grove": "arvoredo", "thicket": "matagal",
    "glade": "clareira", "clearing": "clareira",
    "swamp": "pântano",
    # Natureza — céu/tempo
    "sky": "céu", "heaven": "céu", "heavens": "céus",
    "air": "ar", "wind": "vento", "breeze": "brisa",
    "gust": "rajada", "gale": "vendaval",
    "cloud": "nuvem", "clouds": "nuvens",
    "mist": "neblina", "fog": "névoa", "haze": "bruma",
    "rain": "chuva", "drizzle": "garoa",
    "snow": "neve", "sleet": "neve",
    "ice": "gelo", "frost": "geada",
    "thunder": "trovão", "lightning": "relâmpago",
    "storm": "tempestade", "darkness": "escuridão",
    "shadow": "sombra", "shade": "sombra", "gloom": "penumbra",
    "dark": "escuro", "dusk": "anoitecer", "dusk": "crepúsculo",
    "twilight": "crepúsculo", "murk": "treva",
    # Luz e fogo
    "light": "luz", "radiance": "brilho", "glow": "brilho",
    "gleam": "lampejo", "glimmer": "cintilação",
    "brilliance": "brilhantismo", "flash": "relâmpago",
    "fire": "fogo", "flame": "chama", "blaze": "braseiro",
    "spark": "faísca", "embers": "brasa",
    "heat": "calor", "warmth": "calor",
    "smoke": "fumaça", "ash": "cinza", "ashes": "cinzas",
    "star": "estrela", "stars": "estrelas",
    "sun": "sol", "moon": "lua",
    "dawn": "aurora", "sunrise": "amanhecer",
    "morning": "manhã", "noon": "meio-dia",
    "evening": "tarde", "sunset": "pôr-do-sol",
    "night": "noite", "midnight": "meia-noite",
    # Plantas
    "tree": "árvore", "trees": "árvores",
    "wood": "madeira", "timber": "madeira",
    "leaf": "folha", "leaves": "folhas",
    "branch": "galho", "twig": "galho",
    "root": "raiz", "trunk": "tronco",
    "flower": "flor", "flowers": "flores",
    "blossom": "flor", "bloom": "flor",
    "grass": "grama", "herb": "erva",
    "moss": "musgo", "reed": "junco",
    "berry": "fruta", "fruit": "fruto",
    "seed": "semente", "nut": "noz",
    "rose": "rosa", "lily": "lírio",
    # Animais
    "eagle": "águia", "eagles": "águias",
    "hawk": "falcão", "falcon": "falcão",
    "swan": "cisne", "bird": "pássaro",
    "crow": "corvo", "raven": "corvo",
    "owl": "coruja", "thrush": "tordo",
    "nightingale": "rouxinol",
    "horse": "cavalo", "steed": "corcel", "mare": "égua",
    "hound": "cão", "dog": "cão", "wolf": "lobo",
    "bear": "urso", "fox": "raposa",
    "deer": "cervo", "stag": "veado", "doe": "corça",
    "boar": "javali", "ram": "carneiro",
    "fish": "peixe", "whale": "baleia",
    "serpent": "serpente", "snake": "cobra",
    "dragon": "dragão", "worm": "verme",
    "spider": "aranha", "fly": "mosca",
    "bat": "morcego", "moth": "mariposa",
    # Minerais
    "stone": "pedra", "rock": "rocha",
    "pebble": "seixo", "gravel": "cascalho",
    "sand": "areia", "dust": "poeira",
    "mud": "lama", "clay": "argila",
    "gold": "ouro", "silver": "prata",
    "iron": "ferro", "steel": "aço",
    "copper": "cobre", "bronze": "bronze",
    "crystal": "cristal", "glass": "vidro",
    "gem": "joia", "jewel": "joia", "diamond": "diamante",
    "ruby": "rubi", "sapphire": "safira",
    "pearl": "pérola", "ivory": "marfim",
    # Pessoas — família
    "father": "pai", "mother": "mãe",
    "son": "filho", "daughter": "filha",
    "brother": "irmão", "sister": "irmã",
    "husband": "marido", "wife": "esposa",
    "child": "criança", "children": "crianças",
    "baby": "bebê", "infant": "bebê",
    "grandfather": "avô", "grandmother": "avó",
    "ancestor": "ancestral", "descendant": "descendente",
    "kin": "parente", "kindred": "parentes",
    "family": "família", "clan": "clã",
    # Pessoas — títulos/classes
    "man": "homem", "men": "homens",
    "woman": "mulher", "women": "mulheres",
    "boy": "menino", "girl": "menina",
    "elf": "elfo", "elves": "elfos",
    "elf-man": "elfo", "elf-woman": "elfa",
    "elf-maid": "elfa", "elf-lord": "senhor élfico",
    "elven": "élfico", "elvish": "élfico",
    "hobbit": "hobbit", "halfling": "hobbit",
    "dwarf": "anão", "dwarves": "anões",
    "orc": "orco", "orcs": "orcos",
    "goblin": "goblin", "troll": "trol",
    "ent": "ent", "tree-herder": "ent",
    "wraith": "espectro", "ghost": "fantasma",
    "shade": "espectro", "spirit": "espírito",
    "demon": "demônio", "monster": "monstro",
    "beast": "fera", "creature": "criatura",
    "king": "rei", "queen": "rainha",
    "lord": "senhor", "lady": "senhora",
    "prince": "príncipe", "princess": "princesa",
    "duke": "duque", "earl": "conde",
    "captain": "capitão", "commander": "comandante",
    "leader": "líder", "chief": "chefe",
    "chieftain": "chefe", "high-king": "alto-rei",
    "steward": "guardião", "regent": "regente",
    "warrior": "guerreiro", "soldier": "soldado",
    "knight": "cavaleiro", "rider": "cavaleiro",
    "archer": "arqueiro", "hunter": "caçador",
    "guard": "guarda", "warden": "guardião",
    "watcher": "vigia", "sentinel": "sentinela",
    "messenger": "mensageiro", "herald": "arauto",
    "ambassador": "embaixador",
    "servant": "servo", "slave": "escravo",
    "merchant": "mercador", "craftsman": "artesão",
    "smith": "ferreiro", "carpenter": "carpinteiro",
    "sailor": "marinheiro", "shipwright": "construtor de navios",
    "wizard": "mago", "sorcerer": "feiticeiro",
    "sage": "sábio", "scholar": "estudioso",
    "singer": "cantor", "minstrel": "menestrel",
    "poet": "poeta", "lore-master": "mestre",
    "wanderer": "viajante", "pilgrim": "peregrino",
    "ranger": "patrulheiro", "strider": "passador",
    "exile": "exilado", "outlaw": "fora-da-lei",
    "prisoner": "prisioneiro", "captive": "cativo",
    "friend": "amigo", "friends": "amigos",
    "companion": "companheiro", "ally": "aliado",
    "enemy": "inimigo", "foe": "inimigo",
    "traitor": "traidor", "spy": "espião",
    "people": "povo", "folk": "povo",
    "race": "raça", "kindred": "parentes",
    "host": "exército", "army": "exército",
    "company": "companhia", "band": "grupo",
    "follower": "seguidor", "disciple": "discípulo",
    # Partes do corpo
    "head": "cabeça", "skull": "crânio",
    "face": "rosto", "brow": "testa",
    "eye": "olho", "eyes": "olhos",
    "ear": "orelha", "ears": "orelhas",
    "nose": "nariz", "nostril": "narina",
    "mouth": "boca", "lip": "lábio", "lips": "lábios",
    "tooth": "dente", "teeth": "dentes", "fang": "presa",
    "tongue": "língua", "throat": "garganta",
    "neck": "pescoço", "shoulder": "ombro",
    "arm": "braço", "hand": "mão", "hands": "mãos",
    "finger": "dedo", "thumb": "polegar",
    "palm": "palma", "fist": "punho",
    "leg": "perna", "knee": "joelho",
    "foot": "pé", "feet": "pés", "toe": "dedo-do-pé",
    "body": "corpo", "chest": "peito",
    "heart": "coração", "blood": "sangue",
    "bone": "osso", "marrow": "medula",
    "skin": "pele", "hair": "cabelo",
    "back": "costas", "spine": "coluna",
    "tail": "cauda", "wing": "asa",
    "soul": "alma", "spirit": "espírito",
    "mind": "mente", "thought": "pensamento",
    "will": "vontade", "heart": "coração",
    "voice": "voz", "breath": "respiração",
    # Objetos/artefatos
    "ring": "anel", "rings": "anéis",
    "sword": "espada", "blade": "lâmina",
    "knife": "faca", "dagger": "punhal",
    "bow": "arco", "arrow": "flecha", "arrows": "flechas",
    "spear": "lança", "lance": "lança",
    "shield": "escudo", "buckler": "broquel",
    "helm": "elmo", "helmet": "capacete",
    "armor": "armadura", "mail": "cota de malha",
    "cloak": "manto", "hood": "capuz",
    "robe": "túnica", "garment": "vestimenta",
    "belt": "cinto", "clasp": "fivela",
    "staff": "cajado", "rod": "vara",
    "rope": "corda", "chain": "corrente",
    "key": "chave", "lock": "fechadura",
    "book": "livro", "scroll": "pergaminho",
    "rune": "runa", "letter": "letra",
    "lantern": "lanterna", "candle": "vela",
    "torch": "tocha", "lamp": "lâmpada",
    "crown": "coroa", "scepter": "cetro",
    "banner": "estandarte", "flag": "bandeira",
    "horn": "chifre", "trumpet": "trompete",
    "cup": "cálice", "chalice": "cálice",
    "vessel": "recipiente", "bowl": "tigela",
    "ship": "navio", "boat": "barco",
    "sail": "vela", "oar": "remo",
    "cart": "carroça", "wagon": "vagão",
    "gift": "presente", "prize": "prêmio",
    "treasure": "tesouro", "hoard": "tesouro",
    "jewel": "joia", "ornament": "ornamento",
    # Construções/lugares
    "house": "casa", "home": "lar",
    "hall": "salão", "chamber": "câmara",
    "room": "sala", "vault": "abóbada",
    "tower": "torre", "spire": "espira",
    "fortress": "fortaleza", "stronghold": "fortaleza",
    "castle": "castelo", "citadel": "cidadela",
    "dungeon": "masmorra", "prison": "prisão",
    "city": "cidade", "town": "cidade",
    "village": "vila", "settlement": "assentamento",
    "encampment": "acampamento", "camp": "acampamento",
    "dwelling": "morada", "abode": "morada",
    "haven": "refúgio", "refuge": "refúgio",
    "harbor": "porto", "port": "porto",
    "market": "mercado", "store": "armazém",
    "bridge": "ponte", "arch": "arco",
    "gate": "portão", "door": "porta",
    "wall": "muro", "rampart": "muralha",
    "trench": "vala", "ditch": "fosso",
    "road": "estrada", "street": "rua",
    "path": "caminho", "trail": "trilha",
    # Conceitos abstratos
    "name": "nome", "word": "palavra",
    "speech": "discurso", "language": "língua",
    "tongue": "língua", "dialect": "dialeto",
    "lore": "conhecimento", "wisdom": "sabedoria",
    "knowledge": "conhecimento", "learning": "aprendizado",
    "story": "história", "tale": "conto",
    "song": "canção", "music": "música",
    "melody": "melodia", "harmony": "harmonia",
    "poem": "poema", "verse": "verso",
    "art": "arte", "craft": "ofício",
    "skill": "habilidade", "mastery": "maestria",
    "secret": "segredo", "mystery": "mistério",
    "dream": "sonho", "vision": "visão",
    "omen": "presságio", "prophecy": "profecia",
    "sign": "sinal", "mark": "marca",
    "law": "lei", "rule": "regra", "command": "ordem",
    "oath": "juramento", "vow": "voto",
    "covenant": "aliança", "treaty": "tratado",
    "custom": "costume", "tradition": "tradição",
    "honor": "honra", "glory": "glória",
    "fame": "fama", "renown": "renome",
    "pride": "orgulho", "shame": "vergonha",
    "hope": "esperança", "faith": "fé", "trust": "confiança",
    "love": "amor", "devotion": "devoção",
    "friendship": "amizade", "kinship": "parentesco",
    "loyalty": "lealdade", "duty": "dever",
    "peace": "paz", "rest": "descanso", "calm": "calma",
    "war": "guerra", "battle": "batalha",
    "combat": "combate", "strife": "luta",
    "conflict": "conflito", "siege": "cerco",
    "victory": "vitória", "triumph": "triunfo",
    "defeat": "derrota", "fall": "queda",
    "power": "poder", "might": "força",
    "strength": "força", "force": "força",
    "authority": "autoridade", "dominion": "domínio",
    "rule": "governo", "reign": "reinado",
    "death": "morte", "doom": "destino",
    "fate": "destino", "end": "fim",
    "ruin": "ruína", "destruction": "destruição",
    "life": "vida", "living": "vida",
    "birth": "nascimento", "origin": "origem",
    "beginning": "começo", "start": "início",
    "time": "tempo", "age": "era",
    "year": "ano", "season": "estação",
    "day": "dia", "hour": "hora",
    "memory": "memória", "remembrance": "lembrança",
    "sorrow": "tristeza", "grief": "tristeza",
    "mourning": "luto", "lamentation": "lamento",
    "weeping": "choro", "tears": "lágrimas",
    "pain": "dor", "suffering": "sofrimento",
    "joy": "alegria", "happiness": "felicidade",
    "delight": "prazer", "bliss": "beatitude",
    "wonder": "admiração", "awe": "reverência",
    "beauty": "beleza", "grace": "graça",
    "majesty": "majestade", "splendor": "esplendor",
    "courage": "coragem", "valor": "valor",
    "fear": "medo", "dread": "pavor",
    "terror": "terror", "horror": "horror",
    "wrath": "ira", "anger": "raiva",
    "malice": "malícia", "evil": "mal",
    "good": "bem", "virtue": "virtude",
    "mercy": "misericórdia", "pity": "piedade",
    "justice": "justiça", "truth": "verdade",
    "lies": "mentiras", "deceit": "engano",
    "freedom": "liberdade", "captivity": "cativeiro",
    "exile": "exílio", "wandering": "errância",
    "journey": "jornada", "quest": "missão",
    "adventure": "aventura", "voyage": "viagem",
    # Verbos comuns (como gloss)
    "go": "ir", "come": "vir", "move": "mover",
    "walk": "caminhar", "run": "correr",
    "ride": "cavalgar", "fly": "voar",
    "swim": "nadar", "sail": "navegar",
    "climb": "escalar", "fall": "cair",
    "rise": "subir", "ascend": "subir",
    "descend": "descer", "sink": "afundar",
    "see": "ver", "look": "olhar", "gaze": "contemplar",
    "watch": "vigiar", "observe": "observar",
    "hear": "ouvir", "listen": "escutar",
    "speak": "falar", "say": "dizer", "tell": "contar",
    "call": "chamar", "name": "nomear",
    "answer": "responder", "reply": "responder",
    "sing": "cantar", "chant": "entoar",
    "write": "escrever", "read": "ler",
    "know": "conhecer", "learn": "aprender", "study": "estudar",
    "understand": "compreender", "remember": "lembrar",
    "forget": "esquecer", "think": "pensar",
    "dream": "sonhar", "hope": "esperar",
    "wish": "desejar", "want": "querer",
    "love": "amar", "hate": "odiar",
    "fear": "temer", "dread": "temer",
    "trust": "confiar", "believe": "acreditar",
    "help": "ajudar", "serve": "servir",
    "protect": "proteger", "guard": "guardar",
    "follow": "seguir", "lead": "guiar", "guide": "guiar",
    "seek": "buscar", "find": "encontrar", "search": "procurar",
    "give": "dar", "take": "tomar", "receive": "receber",
    "bring": "trazer", "carry": "carregar",
    "send": "enviar", "throw": "arremessar",
    "make": "fazer", "create": "criar", "craft": "criar",
    "build": "construir", "forge": "forjar",
    "destroy": "destruir", "break": "quebrar",
    "open": "abrir", "close": "fechar",
    "enter": "entrar", "leave": "partir",
    "return": "retornar", "depart": "partir",
    "stay": "ficar", "wait": "esperar",
    "stand": "ficar em pé", "sit": "sentar",
    "lie": "deitar", "sleep": "dormir", "wake": "despertar",
    "live": "viver", "die": "morrer",
    "fight": "lutar", "battle": "batalhar",
    "slay": "matar", "kill": "matar",
    "win": "vencer", "conquer": "conquistar",
    "flee": "fugir", "escape": "escapar",
    "hide": "esconder", "lurk": "espreitar",
    "shine": "brilhar", "gleam": "brilhar", "glow": "brilhar",
    "fall": "cair", "flow": "fluir",
    "grow": "crescer", "bloom": "florescer",
    "eat": "comer", "drink": "beber",
    "carry": "carregar", "lift": "levantar",
    "bind": "amarrar", "free": "libertar",
    "save": "salvar", "rescue": "resgatar",
    "wander": "vagar", "stray": "vagar", "roam": "vagar",
    "call": "chamar", "summon": "convocar",
    "try": "tentar", "strive": "esforçar",
    "labor": "trabalhar", "toil": "trabalhar",
    "dwell": "habitar", "abide": "morar",
    # Adjetivos
    "great": "grande", "mighty": "poderoso", "large": "grande",
    "small": "pequeno", "little": "pequeno", "tiny": "minúsculo",
    "long": "longo", "tall": "alto",
    "short": "curto", "low": "baixo",
    "wide": "largo", "broad": "amplo",
    "narrow": "estreito", "thin": "fino",
    "deep": "profundo", "shallow": "raso",
    "high": "alto", "lofty": "elevado",
    "old": "velho", "ancient": "antigo",
    "young": "jovem", "new": "novo",
    "fast": "rápido", "swift": "veloz", "quick": "rápido",
    "slow": "lento", "still": "quieto",
    "beautiful": "belo", "fair": "belo",
    "lovely": "adorável", "comely": "gracioso",
    "bright": "brilhante", "shining": "resplandecente",
    "light": "claro", "pale": "pálido",
    "dark": "escuro", "black": "negro",
    "white": "branco", "grey": "cinzento",
    "silver": "prateado", "silvery": "prateado",
    "golden": "dourado", "red": "vermelho",
    "blue": "azul", "green": "verde",
    "cold": "frio", "cool": "fresco",
    "hot": "quente", "warm": "morno",
    "hard": "duro", "strong": "forte",
    "soft": "suave", "weak": "fraco",
    "sharp": "afiado", "keen": "afiado",
    "blunt": "rombo", "dull": "opaco",
    "heavy": "pesado", "light": "leve",
    "hollow": "oco", "solid": "sólido",
    "whole": "inteiro", "broken": "quebrado",
    "dead": "morto", "alive": "vivo", "living": "vivo",
    "free": "livre", "bound": "amarrado",
    "lost": "perdido", "found": "encontrado",
    "hidden": "oculto", "secret": "secreto",
    "silent": "silencioso", "quiet": "quieto",
    "loud": "alto", "clear": "claro",
    "true": "verdadeiro", "false": "falso",
    "good": "bom", "evil": "mau", "bad": "ruim",
    "noble": "nobre", "base": "vil",
    "holy": "sagrado", "blessed": "abençoado",
    "cursed": "maldito", "wicked": "perverso",
    "wise": "sábio", "foolish": "tolo",
    "brave": "corajoso", "cowardly": "covarde",
    "kind": "gentil", "cruel": "cruel",
    "proud": "orgulhoso", "humble": "humilde",
    "alone": "sozinho", "lonely": "solitário",
    "single": "único", "only": "único",
    "first": "primeiro", "last": "último",
    "high": "alto", "deep": "profundo",
    "mortal": "mortal", "immortal": "imortal",
    "eternal": "eterno", "endless": "interminável",
    "wholesome": "sadio", "fair": "belo",
    # Direções / pontos cardeais
    "north": "norte", "northern": "norte",
    "south": "sul", "southern": "sul",
    "east": "leste", "eastern": "leste",
    "west": "oeste", "western": "oeste",
    "upper": "superior", "lower": "inferior",
    "inner": "interior", "outer": "exterior",
    # Sufixos e prefixos (como gloss)
    "prefix": "prefixo", "suffix": "sufixo",
    "ending": "sufixo", "augmentative suffix": "sufixo aumentativo",
    "adjective suffix": "sufixo adjetivo",
    "noun suffix": "sufixo nominal",
    # Numerais ordinais
    "first": "primeiro", "second": "segundo",
    "third": "terceiro", "fourth": "quarto",
    "fifth": "quinto", "sixth": "sexto",
    "seventh": "sétimo", "eighth": "oitavo",
    "ninth": "nono", "tenth": "décimo",
    "one": "um", "two": "dois", "three": "três",
    "four": "quatro", "five": "cinco",
    "six": "seis", "seven": "sete",
    "eight": "oito", "nine": "nove", "ten": "dez",
    "twelve": "doze", "hundred": "cem",
    "many": "muitos", "few": "poucos",
    "all": "todos", "none": "nenhum",
    "double": "dobro", "half": "metade",
}

SPEECH_TO_CLASS = {
    "noun": "substantivo", "n": "substantivo",
    "verb": "verbo", "vb": "verbo", "v": "verbo",
    "adj": "adjetivo", "adjective": "adjetivo",
    "adv": "advérbio", "adverb": "advérbio",
    "prefix": "prefixo", "suffix": "sufixo",
    "prep": "preposição", "preposition": "preposição",
    "conj": "conjunção", "conjunction": "conjunção",
    "pron": "pronome", "pronoun": "pronome",
    "interj": "interjeição",
    "particle": "partícula", "article": "artigo",
    "masc-name": "nome-próprio", "fem-name": "nome-próprio",
    "place-name": "nome-próprio", "proper-name": "nome-próprio",
    "phrase": "expressão",
}

SKIP_GLOSSES = {
    "[unglossed]", "?", "??", "???", "[?]",
    "adjective suffix", "noun suffix", "verb suffix",
    "augmentative suffix", "diminutive suffix",
    "adjectival prefix", "verbal prefix", "nominal prefix",
}


def clean_gloss(gloss: str) -> str:
    g = gloss.strip()
    g = re.sub(r"\s*\(.*?\)", "", g)  # remove parenthetical
    g = g.lstrip("*").strip()         # remove leading asterisk
    g = g.rstrip(".,;:!?").strip()
    return g.lower()


def try_translate(gloss: str) -> str | None:
    """Tenta traduzir um gloss para português usando múltiplas estratégias."""
    g = clean_gloss(gloss)
    if not g or g in SKIP_GLOSSES:
        return None

    # 1. Match direto
    if g in EN_PT:
        return EN_PT[g]

    # 2. Cada parte separada por vírgula/ponto-vírgula/ou
    parts = re.split(r"[,;/]| or | and ", g)
    for part in parts:
        part = part.strip()
        if part in EN_PT:
            return EN_PT[part]

    # 3. Primeira palavra do gloss composto
    first = g.split()[0].strip()
    if first in EN_PT and len(first) > 1:
        return EN_PT[first]

    # 4. Última palavra (ex: "petty dwarf" → "dwarf")
    last = g.split()[-1].strip()
    if last in EN_PT and len(last) > 2:
        return EN_PT[last]

    return None


def get_class(speech: str) -> str:
    if not speech:
        return "substantivo"
    return SPEECH_TO_CLASS.get(speech.strip().lower(), "substantivo")


# ─── Parse ────────────────────────────────────────────────────────────────────
print("Carregando eldamo-data.xml...")
tree = ET.parse("eldamo-data.xml")
root = tree.getroot()
print("Extraindo palavras Sindarin (l='s')...")

# Coleta: word elements com l='s', sem deprecated, com gloss traduzível
raw_entries: dict[str, list[dict]] = {}  # pt_word -> lista de candidatos

total = skipped = 0
for word_elem in root.iter("word"):
    if word_elem.get("l") != "s":
        continue
    total += 1

    # Pular depreciadas
    if word_elem.find("deprecated") is not None:
        skipped += 1
        continue

    sd_form = word_elem.get("v", "").strip()
    gloss_en = word_elem.get("gloss", "").strip()
    speech = word_elem.get("speech", "")
    source = word_elem.get("source", "")

    if not gloss_en or not sd_form:
        skipped += 1
        continue

    pt_word = try_translate(gloss_en)
    if pt_word is None:
        skipped += 1
        continue

    classe = get_class(speech)
    is_reconstructed = gloss_en.startswith("*")
    has_source = bool(source)

    entry = {
        "sindarin": sd_form,
        "classe": classe,
        "gloss_en": gloss_en,
        "has_source": has_source,
        "reconstructed": is_reconstructed,
    }

    if pt_word not in raw_entries:
        raw_entries[pt_word] = []
    raw_entries[pt_word].append(entry)

print(f"  Total Sindarin: {total} | Ignorados: {skipped}")
print(f"  PT palavras únicas: {len(raw_entries)}")

# ─── Selecionar melhor candidato por palavra PT ───────────────────────────────
def score_entry(e: dict) -> int:
    """Maior score = melhor candidato."""
    s = 0
    if e["has_source"]:      s += 10
    if not e["reconstructed"]: s += 5
    if "*" not in e["sindarin"]: s += 3
    if "?" not in e["sindarin"]: s += 2
    return s

best_entries: dict[str, dict[str, str]] = {}
for pt_word, candidates in raw_entries.items():
    best = max(candidates, key=score_entry)
    best_entries[pt_word] = {
        "sindarin": best["sindarin"],
        "classe": best["classe"],
    }

print(f"  Entradas selecionadas: {len(best_entries)}")

# ─── Carregar léxico PT handcrafted (ANTES de qualquer modificação) ───────────
import os
existing_path = "data/pt-sindarin.json"
handcrafted_path = "data/pt-sindarin-handcrafted.json"

# Primeiro run: se não existe backup, o existente É o handcrafted → salvá-lo
if not os.path.exists(handcrafted_path) and os.path.exists(existing_path):
    import shutil
    shutil.copy(existing_path, handcrafted_path)
    print(f"Backup handcrafted salvo em {handcrafted_path}")

# Ler o handcrafted (fonte da verdade para palavras já conhecidas)
handcrafted: dict[str, dict[str, str]] = {}
if os.path.exists(handcrafted_path):
    with open(handcrafted_path, encoding="utf-8") as f:
        handcrafted = cast(dict[str, dict[str, str]], json.load(f))
    print(f"\nLexico handcrafted: {len(handcrafted)} entradas")

# Mesclar: handcrafted SEMPRE vence; Eldamo só adiciona palavras NOVAS
merged: dict[str, dict[str, str]] = {}
for pt_word, entry in best_entries.items():
    if pt_word not in handcrafted:   # só adiciona se NÃO está no handcrafted
        merged[pt_word] = entry
merged.update(cast(dict[str, dict[str, str]], handcrafted))  # handcrafted sobrescreve tudo

new_from_eldamo = len(merged) - len(handcrafted)
print(f"Novas palavras do Eldamo: {new_from_eldamo}")
print(f"Total apos mesclagem: {len(merged)} entradas")

# Ordenar alfabeticamente
output = dict(sorted(merged.items()))

with open(existing_path, "w", encoding="utf-8") as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

print(f"\n[OK] Salvo em {existing_path} com {len(output)} entradas.")

# ─── Estatísticas ──────────────────────────────────────────────────────────────
classes = Counter(v["classe"] for v in output.values())
print("\nDistribuicao por classe:")
for k, v in sorted(classes.items(), key=lambda x: -x[1]):
    print(f"  {k:20s}: {v:4d}")

print("\nAmostra de novas entradas (Eldamo):")
new_keys: list[str] = [k for k in best_entries if k not in handcrafted]
new_keys = new_keys[:20]
for k in new_keys:
    print(f"  {k:25s} -> {best_entries[k]['sindarin']}")
