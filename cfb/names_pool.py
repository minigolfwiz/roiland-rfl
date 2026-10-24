FIRST_NAMES = [
 # Anglo/Western
 "James","Michael","David","John","Robert","William","Ryan","Tyler","Brandon","Cody",
 "Emily","Sarah","Jessica","Ashley","Megan","Lauren","Hannah","Grace","Chloe","Olivia",
 "Alex","Jordan","Taylor","Morgan","Casey","Riley","Cameron","Avery","Reese","Peyton",
 # Latino/Hispanic
 "Carlos","Miguel","Javier","Diego","Rafael","Alejandro","Mateo","Santiago","Emilio","Andres",
 "Sofia","Valentina","Camila","Isabella","Ximena","Maria","Lucia","Gabriela","Daniela","Paola",
 # African/African-American
 "Malik","Jamal","Darnell","Marcus","DeShawn","Terrence","Isaiah","Elijah","Andre","Xavier",
 "Aaliyah","Imani","Nia","Jasmine","Destiny","Zuri","Amara","Kayla","Tiana","Aisha",
 # Middle Eastern
 "Omar","Yusuf","Ahmed","Karim","Tariq","Hassan","Rami","Zayn","Amir","Faisal",
 "Layla","Yasmin","Amina","Noor","Fatima","Zainab","Rania","Salma","Dina","Huda",
 # East Asian
 "Wei","Jian","Hiroshi","Kenji","Takeshi","Min-jun","Jae-won","Haruto","Ryo","Sora",
 "Mei","Yuki","Ling","Ji-woo","Aiko","Sakura","Xia","Yumi","Hana","Bo",
 # South Asian
 "Arjun","Ravi","Vikram","Rohan","Aditya","Ishaan","Karan","Nikhil","Sanjay","Aarav",
 "Priya","Anjali","Divya","Neha","Kavya","Ananya","Meera","Pooja","Riya","Isha",
 # Slavic/Eastern European
 "Dmitri","Ivan","Nikolai","Sergei","Pavel","Viktor","Boris","Andrei","Yuri","Mikhail",
 "Anastasia","Katarina","Olga","Irina","Natasha","Svetlana","Elena","Petra","Zofia","Milena",
 # Nordic
 "Erik","Bjorn","Lars","Nils","Sven","Magnus","Anders","Henrik","Gustav","Oskar",
 "Freya","Ingrid","Astrid","Sigrid","Elsa","Solveig","Liv","Karin","Maja","Saga",
 # Pacific Islander / Polynesian
 "Kai","Manu","Tane","Sione","Filipe","Mosese","Levani","Tevita","Pita","Aisake",
 "Leilani","Moana","Nalani","Kalani","Malia","Sina","Litia","Ana","Sarona","Vaiana",
 # Native American
 "Dakota","Hawk","Chayton","Kai","Tokala","Mato","Wahchinksapa","Elan","Nayati","Tocho",
 "Winona","Halona","Kimimela","Onawa","Ayasha","Wamblee","Aiyana","Wenona","Doba","Sora",
 # Unisex/modern
 "Quinn","Skyler","River","Sage","Rowan","Phoenix","Justice","Ariel","Dakota","Emerson",
]

LAST_NAMES = [
 "Smith","Johnson","Williams","Brown","Jones","Garcia","Miller","Davis","Rodriguez","Martinez",
 "Hernandez","Lopez","Gonzalez","Wilson","Anderson","Thomas","Taylor","Moore","Jackson","Martin",
 "Lee","Perez","Thompson","White","Harris","Sanchez","Clark","Ramirez","Lewis","Robinson",
 "Walker","Young","Allen","King","Wright","Scott","Torres","Nguyen","Hill","Flores",
 "Green","Adams","Nelson","Baker","Hall","Rivera","Campbell","Mitchell","Carter","Roberts",
 "Patel","Shah","Kumar","Singh","Sharma","Khan","Ahmed","Ali","Hassan","Ibrahim",
 "Kim","Park","Choi","Yang","Wang","Chen","Zhang","Liu","Wu","Huang",
 "Tanaka","Suzuki","Sato","Watanabe","Yamamoto","Nakamura","Ito","Kobayashi",
 "Okafor","Adebayo","Mensah","Diallo","Kamau","Mwangi","Osei","Boateng","Abara","Chukwu",
 "Kowalski","Nowak","Wojcik","Petrov","Ivanov","Volkov","Sokolov","Popov","Novak","Horvat",
 "Andersen","Hansen","Larsen","Nielsen","Johansson","Eriksson","Karlsson","Berg","Lindqvist",
 "Tupou","Fifita","Taufa","Havili","Mahe","Kaho","Latu","Vaka","Fonoti","Iosefo",
 "Begay","Yazzie","Runningwater","Whitehorse","Bluehorse","Redcloud","Standing Bear","Little Elk",
 "Silva","Costa","Santos","Oliveira","Pereira","Ferreira","Almeida","Rocha","Carvalho",
 "Dubois","Bernard","Laurent","Moreau","Girard","Rousseau","Fontaine","Chevalier",
 "Muller","Schmidt","Schneider","Fischer","Weber","Meyer","Wagner","Becker","Hoffmann",
]

POSITIONS = {
    "QB": 4, "RB": 6, "WR": 10, "TE": 5, "OL": 15,
    "DL": 12, "LB": 10, "CB": 10, "S": 7,
    "K": 2, "P": 2, "LS": 2,
}
OFFENSE_POS = ["QB","RB","WR","TE","OL"]
DEFENSE_POS = ["DL","LB","CB","S"]
ST_POS = ["K","P","LS"]

assert sum(POSITIONS.values()) == 85
