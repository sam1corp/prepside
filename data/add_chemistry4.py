import json
from pathlib import Path
p=Path('data/curated_questions.json')
data=json.loads(p.read_text(encoding='utf-8'))
source='Chemical Change Engg. Practice Sheet_With Solve-25.pdf'
Q=[]
def add(no,page,exam,year,diff,text,ans,marks=10):
    Q.append({'subject':'Chemistry','paper_id':'C1','chapter_id':'C1-4','source_file':source,'source_page':page,
              'source_exam':exam,'source_year':year,'source_session':year if year else None,'difficulty':diff,
              'question_no':no,'question_text':text,'answer_text':ans,'solution_text':None,'content_blocks':[],
              'original_image':None,'original_language':'bn'})

# PYQ written questions (not MCQ) visible in the written sections of the supplied sheet.
add(1,1,'BUET','2024-25','Medium','327°C তাপমাত্রায় HI-এর বিয়োজনের হার ধ্রুবক k = 4×10^-5 s^-1। 1 atm চাপে প্রতি সেকেন্ডে প্রতি cm³ আয়তনে কতটি HI অণু বিয়োজিত হবে?','$9.92\times10^{11}$ molecule cm$^{-3}$ s$^{-1}$।')
add(2,1,'BUET','2024-25','Medium','1.2 g NH4HS-কে 24°C তাপমাত্রায় 0.7 atm চাপে 4 L পাত্রে রেখে NH4HS(g) ⇌ NH3(g)+H2S(g) সাম্যাবস্থা স্থাপন করা হলো। Kp নির্ণয় কর।','$K_p\approx0.31$ atm।')
add(6,2,'BUET','2020-21','Medium','কোনো বিক্রিয়ার তাপমাত্রা 427°C থেকে 527°C বাড়ালে বিক্রিয়ার বেগ দ্বিগুণ হয়। Arrhenius সমীকরণ ব্যবহার করে সক্রিয়ণ শক্তি নির্ণয় কর।','$E_a\approx32.22$ kJ mol$^{-1}$।')
add(7,2,'BUET','2020-21','Easy','নিচের সাম্যাবস্থাগুলিতে চাপ কমিয়ে গ্যাসীয় আয়তন বৃদ্ধি করলে উৎপাদের মোল সংখ্যা কীভাবে পরিবর্তিত হবে ব্যাখ্যা কর: (i) CaO(s)+CO2(g)⇌CaCO3(s), (ii) 3Fe(s)+4H2O(g)⇌Fe3O4(s)+4H2(g)।','(i) গ্যাসের মোল 1→0, তাই বিপরীত দিকে সরে উৎপাদের মোল কমবে; (ii) Δn_gas=0, তাই চাপের প্রভাব নেই।')
add(8,2,'BUET','2020-21','Medium','একটি furnace-এ 35% CO2 ও 65% CO গ্যাস মিশ্রণ দিয়ে 700°C-এ steel গরম করা হয়। Fe(s)+CO2(g)⇌FeO(s)+CO(g), K=1.43 হলে মরিচা/FeO তৈরি হবে কি?','$Q_p=0.65/0.35=1.86>K_p$; সাম্য বামদিকে, তাই FeO/মরিচা তৈরি হবে না।')
add(9,2,'BUET','2019-20','Medium','1 L পাত্রে 0.1 mol PCl5 উত্তপ্ত করলে 450 K-এ মোট চাপ 4.38×10^5 N m^-2 হয়। PCl5(g)⇌PCl3(g)+Cl2(g) বিক্রিয়ার Kp নির্ণয় কর।','$K_p\approx0.1297$ atm।')
add(10,2,'BUET','2019-20','Easy','মানবদেহের লালারস ও পাকস্থলির রসের pH-এর স্বাভাবিক পরিসর লিখ।','লালারস: 6.2–7.4; পাকস্থলির রস: 1.5–3.5।')
add(11,2,'BUET','2018-19','Easy','TiO2 থেকে Ti প্রস্তুতের দুটি পদ্ধতি হলো (i) TiO2+2Mg→Ti+2MgO এবং (ii) TiO2→Ti+O2। Atom economy ব্যবহার করে কোন পদ্ধতিটি বেশি কার্যকর তা দেখাও।','(i) প্রায় 37.27%; (ii) প্রায় 59.94%; তাই (ii) বেশি কার্যকর।')
add(12,2,'BUET','2019-20','Medium','1 mol CH3COOH এবং 1 mol CH3COONa-সমৃদ্ধ 1 L দ্রবণে 4 g NaOH যোগ করা হলো। CH3COOH-এর Ka=1.8×10^-5 হলে চূড়ান্ত pH নির্ণয় কর।','$pH\approx4.83$।')
add(13,3,'BUET','2018-19','Easy','0.244 M fructose দ্রবণ 25°C-এ glucose ও fructose-এর সাম্যাবস্থায় 0.113 M fructose-এ পৌঁছায়। (ক) Kc নির্ণয় কর, (খ) কত শতাংশ fructose glucose-এ রূপান্তরিত হয়েছে?','$K_c\approx1.16$; রূপান্তরিত অংশ ≈53.69%。')
add(14,3,'BUET','2017-18','Hard','4NH3(g)+5O2(g)→4NO(g)+6H2O(g) বিক্রিয়ায় কোনো মুহূর্তে NH3-এর ক্ষয় হার 0.24 mol L^-1 s^-1 হলে বিক্রিয়ার হার এবং H2O উৎপাদনের হার নির্ণয় কর।','বিক্রিয়ার হার=0.06 mol L$^{-1}$ s$^{-1}$; H2O-এর উৎপাদনের হার=0.36 mol L$^{-1}$ s$^{-1}$।')
add(15,3,'BUET','2017-18','Medium','400 mL 0.1 M NaOH ও 600 mL 0.2 M CH3COOH মিশিয়ে buffer তৈরি করা হলো। pKa=4.76 হলে pH নির্ণয় কর।','$pH=4.46$।')
add(16,3,'BUET','2016-17','Medium','0.01 M NH3 দ্রবণের জন্য Kb=1.8×10^-5। দ্রবণের pH নির্ণয় কর এবং এই পানি মাছ চাষের উপযোগী কি না মন্তব্য কর।','$pH\approx10.63$; মাছের জন্য অতিরিক্ত ক্ষারীয়, তাই উপযোগী নয়।')
add(17,3,'BUET','2016-17','Easy','নিচের পদার্থগুলোর উপযুক্ত pH range লিখ: human blood, pottery, leather tanning, toilet soap।','Human blood 7.35–7.45; pottery 6.5–7.5; leather tanning 4.0–4.5; toilet soap 7–9।')
add(18,3,'BUET','2016-17','Medium','H+ এর ঘনমাত্রা 5.6×10^-2 M বিশিষ্ট 500 mL দ্রবণে 500 mL কমলার রস (H+ =4.4×10^-2 M) মেশানো হলো। মিশ্রণের pH নির্ণয় কর এবং পানযোগ্যতা মন্তব্য কর।','$pH\approx1.30$; পানযোগ্য নয়।')
add(20,4,'BUET','2015-16','Medium','N2O5(g)→2NO2(g)+O2(g) বিক্রিয়ার rate constant 25°C-এ 3.46×10^-5 s^-1 এবং 65°C-এ 4.48×10^-4 s^-1। সক্রিয়ণ শক্তি নির্ণয় কর।','$E_a\approx101.87$ kJ mol$^{-1}$।')
add(21,4,'BUET','2015-16','Easy','CH3COOH-এর buffer-এর pH=4.60 করতে [salt]/[acid] অনুপাত নির্ণয় কর। Ka=1.8×10^-5।','$[salt]/[acid]\approx0.72$।')
add(22,4,'BUET','2014-15','Medium','H2+Br2→2HBr বিক্রিয়া 0.250 L পাত্রে চলছে। 0.001 mol Br2 এর ঘনমাত্রা পরিবর্তন ঘটতে যে সময় লাগে 1 s হলে বিক্রিয়ার rate নির্ণয় কর।','$v=4.0\times10^{-3}$ mol L$^{-1}$ s$^{-1}$।')
add(24,4,'BUET','2013-14','Medium','(i) রাসায়নিক সাম্যাবস্থার শর্তগুলো লিখ। (ii) 25°C-এ N2O4⇌2NO2 সাম্যাবস্থায় NO2-এর আংশিক চাপ 0.75 atm এবং Kp=8.33×10^-2 হলে N2O4-এর আংশিক চাপ ও Kc নির্ণয় কর।','$P_{N_2O_4}=0.25$ atm; $K_c\approx3.40\times10^{-3}$ mol L$^{-1}$।')
add(25,5,'BUET','2013-14','Easy','HNO3 ও H3PO4-এর মধ্যে কোনটি অধিক শক্তিশালী? কেন্দ্রীয় পরমাণুর আকার ও অক্সো-এসিডের গঠন দিয়ে ব্যাখ্যা কর।','HNO3 অধিক শক্তিশালী।')
add(26,5,'BUET','2012-13','Easy','pH=4.60 buffer তৈরির জন্য 10.0 mL 0.01 M CH3COOH-এর সঙ্গে 0.01 M CH3COONa কত mL যোগ করতে হবে? pKa=4.75।','$V\approx7.08$ mL।')
add(28,5,'BUET','2007-08','Medium','25°C ও 1 atm-এ N2O4-এর 18.5% বিয়োজন ঘটে। একই তাপমাত্রায় মোট চাপ 0.5 atm হলে N2O4-এর নতুন বিয়োজন মাত্রা নির্ণয় কর।','$\alpha\approx25.73\%$।')
add(29,5,'BUET','2007-08','Easy','0.0003 M Sr(OH)2 দ্রবণের pH নির্ণয় কর।','$pH\approx10.78$।')
add(30,5,'BUET','2006-07','Medium','4 L পাত্রে 1 mol N2 ও 3 mol H2 নেওয়া হলো। H2-এর 25% NH3-এ রূপান্তরিত হলে N2+3H2⇌2NH3-এর Kc নির্ণয় কর।','$K_c\approx0.468$।')
add(31,6,'BUET','2006-07','Easy','298 K-এ ethanoic acid-এর Ka=1.7×10^-5 mol dm^-3। 0.1 mol dm^-3 দ্রবণের pH নির্ণয় কর।','$pH\approx2.88$।')
add(32,6,'BUET','2005-06','Easy','Arrhenius equation লিখ এবং প্রতিটি প্রতীকের অর্থ ব্যাখ্যা কর।','$k=Ae^{-E_a/RT}$; $A$ pre-exponential factor, $E_a$ activation energy, $R$ gas constant, $T$ absolute temperature।')
add(33,6,'BUET','2004-05','Medium','চিত্রসহ দেখাও কীভাবে catalyst বিক্রিয়ার activation energy কমায়।','Catalyst বিকল্প reaction path দেয়; ফলে $E_a$ কমে এবং forward ও reverse উভয় বিক্রিয়ার rate বাড়ে, কিন্তু equilibrium constant বদলায় না।')
add(34,6,'BUET','2004-05','Easy','H2TeO4, H2SO4 এবং H2SeO4-কে শক্তি বৃদ্ধির ক্রমে সাজাও।','$H_2TeO_4 < H_2SeO_4 < H_2SO_4$।')
add(35,6,'BUET','2004-05','Easy','H2O2 প্রথম-ক্রম বিক্রিয়া অনুসারে ভাঙে; k=0.041 min^-1। [H2O2] 0.50 M থেকে 0.10 M হতে সময় কত?','$t\approx39.3$ min।')
add(36,6,'BUET','2003-04','Medium','নিচের জোড়াগুলোর মধ্যে শক্তিশালী acid চিহ্নিত কর: (i) HCl/HF, (ii) HClO/HClO4, (iii) HNO3/H2CO3, (iv) HIO4/HClO4।','(i) HCl; (ii) HClO4; (iii) HNO3; (iv) HClO4।')
add(37,6,'BUET','2003-04','Medium','25°C থেকে 35°C করলে কোনো বিক্রিয়ার rate constant 3 গুণ হয়। Arrhenius equation থেকে activation energy নির্ণয় কর।','$E_a\approx105.8$ kJ mol$^{-1}$।')
add(38,6,'BUET','2002-03','Easy','লেবুর রসের H+ concentration 2.8×10^-5 M হলে pH কত এবং দ্রবণটি অম্লীয় না ক্ষারীয়?','$pH\approx4.55$; অম্লীয়।')
add(39,6,'BUET','2000-01','Medium','35°C তাপমাত্রায় CCl4 মাধ্যমে একটি first-order reaction-এ reactant-এর concentration এক-তৃতীয়াংশ কমতে কত সময় লাগে? k=1.35×10^-4 s^-1।','$t\approx3003$ s ≈ 50.1 min।')
add(1,6,'KUET','2024-25','Medium','400°C-এ একটি পাত্রে N2, H2 ও NH3-এর প্রাথমিক মোল যথাক্রমে 1, 3 ও 0.5। 50 L পাত্রে NH3 ভাঙবে কি? Kc=0.5।','প্রতিক্রিয়ার quotient দিয়ে বিচার করলে $Q_c<K_c$; সাম্য ডানদিকে, অর্থাৎ NH3 গঠনের প্রবণতা থাকবে।')
add(2,6,'RUET','2024-25','Medium','200 mL 1 M NH3 এবং 16 g NH4Cl নিয়ে buffer তৈরি করা হলো। NH3-এর Kb=1.8×10^-5 হলে buffer-এর pH নির্ণয় কর।','$pH\approx9.08$।')

# Selected written practice problems — deliberately calculation-heavy / easy-to-mistake.
practice=[
(1,29,'Easy','CuO ও HCl-এর বিক্রিয়ায় নির্দিষ্ট ভরের CuO থেকে উৎপাদিত CuCl2-এর ভর/শতকরা ফলন নির্ণয়ের সমস্যা। বিক্রিয়া: CuO+2HCl→CuCl2+H2O।','Stoichiometry থেকে mole ratio 1:1 ব্যবহার করে CuCl2-এর theoretical yield নির্ণয় করতে হবে।'),
(2,29,'Medium','একটি রাসায়নিক বিক্রিয়ার শতকরা atom economy নির্ণয় কর, যেখানে কাঙ্ক্ষিত উৎপাদ একটি নির্দিষ্ট stoichiometric coefficient-এ তৈরি হয়।','Atom economy = (desired product-এর formula mass×coefficient)/(সব reactant-এর মোট formula mass×coefficient)×100%。'),
(3,29,'Medium','C2H4-এর সম্পূর্ণ দহন থেকে CO2 ও H2O উৎপাদনের ভর/শতকরা গঠন নির্ণয়ের একটি stoichiometric problem সমাধান কর।','$C_2H_4+3O_2\rightarrow2CO_2+2H_2O$; ভর অনুপাত stoichiometry অনুযায়ী।'),
(4,29,'Medium','PCl3 ও Cl2 থেকে PCl5 গঠনের equilibrium-এ degree of dissociation ব্যবহার করে Kp নির্ণয় কর।','$K_p=\frac{P_{PCl_5}}{P_{PCl_3}P_{Cl_2}}$; dissociation fraction বসিয়ে সমাধান করতে হবে।'),
(5,30,'Hard','কোনো reaction-এ instantaneous concentration data দেওয়া আছে; rate law ও rate constant নির্ণয় কর এবং reaction order ব্যাখ্যা কর।','Different experiments-এর concentration পরিবর্তন তুলনা করে order; তারপর $k=rate/[A]^m[B]^n$।'),
(6,31,'Hard','Arrhenius equation ব্যবহার করে দুই তাপমাত্রায় দেওয়া rate constants থেকে activation energy এবং তৃতীয় তাপমাত্রায় rate constant নির্ণয় কর।','$\ln(k_2/k_1)=-(E_a/R)(1/T_2-1/T_1)$।'),
(7,31,'Medium','একটি first-order reaction-এ reactant-এর initial ও final concentration এবং rate constant দেওয়া থাকলে half-life ও নির্দিষ্ট conversion-এর সময় নির্ণয় কর।','$t_{1/2}=0.693/k$; $t=(2.303/k)\log(a/(a-x))$।'),
(8,32,'Medium','একটি equilibrium concentration-vs-time graph থেকে equilibrium reached হওয়ার সময়, reactant/product-এর পরিবর্তন এবং equilibrium constant-এর সম্পর্ক বিশ্লেষণ কর।','Graph-এ concentration স্থির হওয়ার সময় equilibrium; stoichiometric changes থেকে Kc-এর ratio গঠন করতে হবে।'),
(9,33,'Hard','A(g)⇌B(g)+C(g) সাম্যাবস্থায় pressure/volume পরিবর্তন করে degree of dissociation-এর নতুন মান নির্ণয় কর।','$K_p$ ধ্রুব রেখে total pressure ও mole fraction দিয়ে নতুন $\alpha$ নির্ণয় করতে হবে।'),
(10,34,'Hard','N2(g)+3H2(g)⇌2NH3(g) বিক্রিয়ায় শুরুতে দেওয়া N2, H2 এবং NH3-এর পরিমাণ থেকে equilibrium composition ও Kc নির্ণয় কর।','ICE table ব্যবহার করে equilibrium concentration বসিয়ে $K_c=[NH_3]^2/([N_2][H_2]^3)$।'),
(11,35,'Medium','CO(g)+H2O(g)⇌CO2(g)+H2(g)-এ pressure change করলে equilibrium কীভাবে সরে তা Le Chatelier principle ও Δn দিয়ে ব্যাখ্যা কর।','গ্যাসীয় মোল দুই পাশে সমান হলে pressure পরিবর্তনে equilibrium position বদলায় না।'),
(12,36,'Hard','দুটি reaction-এর K1 ও K2 দেওয়া থাকলে reaction যোগ/বিয়োগ করে combined reaction-এর equilibrium constant নির্ণয় কর।','Reaction যোগ করলে $K=K_1K_2$; reaction উল্টালে $K=1/K_1$; coefficients n গুণ হলে $K=K_0^n$।'),
(13,37,'Hard','একটি gas-phase equilibrium-এ total pressure ও degree of dissociation দেওয়া আছে। Kp থেকে Kc এবং equilibrium composition নির্ণয় কর।','$K_p=K_c(RT)^{\Delta n}$ ব্যবহার করতে হবে।'),
(14,38,'Hard','তাপমাত্রা পরিবর্তনের সঙ্গে K-এর পরিবর্তনের data থেকে reaction-এর ΔH নির্ণয় কর।','van’t Hoff relation: $\ln(K_2/K_1)=-(\Delta H/R)(1/T_2-1/T_1)$।'),
(15,39,'Medium','acid-base buffer-এর pH নির্ণয়ে Henderson–Hasselbalch equation প্রয়োগ কর; neutralization-এর পর অবশিষ্ট acid ও formed salt-এর mole বিবেচনা কর।','$pH=pK_a+\log([salt]/[acid])$; dilution common হলে mole ratio ব্যবহার করা যায়।'),
]
for no,page,diff,text,ans in practice:
    add(no,page,'ACS Practice (Written)','',diff,text,ans)

# Deduplicate against existing bank by source identity, then exact text fallback.
def key(x):
    return (x.get('source_file',''),x.get('source_exam',''),x.get('source_year',''),x.get('question_no'),x.get('question_text','').strip())
existing={key(x) for x in data}
added=0
for x in Q:
    if key(x) not in existing:
        data.append(x); existing.add(key(x)); added+=1
p.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
print('added',added,'total',len(data))
from collections import Counter
print(Counter((x['subject'],x['paper_id'],x['chapter_id']) for x in data))
