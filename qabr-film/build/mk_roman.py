import json, re
R = """Ae ghafil insaan! Zara apni qabr ka tasawwur kar!
Ae ghafil insaan! Zara chand lamhon ke liye tasawwur kar...
Tasawwur kar ke tu mar chuka hai!
Teri saansein ruk chuki hain,
Teri aankhein hamesha ke liye band ho chuki hain,
Tere ghar wale tere ard-gird baith kar ro rahe hain.
Koi tere chehre ko aakhri baar dekh raha hai,
Koi tujhe awaaz de raha hai,
Magar ab tu kisi ko jawab nahi de sakta.
Tujhe ghusl diya ja chuka hai,
Tere jism par safed kafan daal diya gaya hai,
Tere ghar wale tujhe kandhon par utha kar qabristan le ja chuke hain.
Tujh par namaz-e-janaza ada ki ja chuki hai,
Aur ab tujhe is tareek qabr mein utaara ja raha hai.
Ae insaan! Zara tasawwur kar...
Ab tere jism par mitti daali ja rahi hai.
Ek ek mutthi mitti tere upar gir rahi hai.
Tere apne tujhe dafan kar ke waapas ja rahe hain.
Tu awaazein sun raha hai,
Qadmon ki aahat sun raha hai,
Lekin ab tere saath koi nahi.
Ab tasawwur kar ke qabr ka imtihaan shuru ho chuka hai.
Munkar aur Nakeer tere paas aate hain
Aur tujh se sawaal karte hain.
Ab na tere paas daulat hai, na taaqat,
Na koi sifarish jis par tu bharosa kar sake.
Ab tere saamne sirf tere a'maal hain.
Aur ae insaan!
Zara yaad kar... tu duniya mein kaise zindagi guzarta tha?
Tu har chhoti si baat par logon ko gaaliyan deta tha.
Kisi ne tujhe zara sa kuch keh diya
Tou tu us ki maa behan tak pahunch jaata tha.
Tu logon ki izzat uchhaalta tha,
Kamzoron ko zaleel karta tha,
Apne doston ke dil dukhata tha.
Koi tujhe samjhaata to tu kehta tha,
"Meri zubaan hai,
Main jo chahoon bolun!"
Lekin aaj kahan hai teri woh zubaan?
Aaj tu aik lafz bhi nahi bol sakta.
Aaj tu kisi ko gaali nahi de sakta.
Aaj tu kisi ko jawab nahi de sakta.
Ae insaan! Kya tujhe yaad hai woh shakhs
Jise tu ne sab ke saamne zaleel kiya tha?
Kya tujhe yaad hai woh ghareeb
Jise tu ne gaali di thi?
Kya tujhe yaad hai woh insaan
Jis ki aankhon mein tere alfaaz ne aansoo bhar diye the?
Aaj tu inhi lamhon ko yaad kar ke pachta raha hai.
Kaash! Tu us waqt apni zubaan rok leta.
Kaash! Tu us insaan se maafi maang leta.
Kaash! Tu samajh jaata ke kisi ka dil dukhana
Koi mamooli baat nahi.
Mere bhai! Rasoolullah sallallahu alaihi wasallam ne farmaya:
Musalman ko gaali dena fisq hai.
(Sahih Bukhari o Sahih Muslim)
To phir soch! Jis zubaan se tu Allah ka zikr kar sakta tha,
Durood shareef parh sakta tha,
Quran ki tilawat kar sakta tha,
Usi zubaan se tu ne logon ke dil kyun tode?
Ae mere bhai! Abhi waqt hai.
Tu zinda hai. Teri saansein chal rahi hain.
Abhi apne Rab se sachchi tauba kar le.
Jin logon ko tu ne takleef pahunchai hai,
Un se maafi maang le.
Apni zubaan ko paak kar le.
Kisi ki izzat mat uchhaal,
Kisi ko gaali mat de,
Kisi ke dil ko mat tod.
Kyunke...
Aik din tujhe bhi isi qabr mein
Utarna hai.
Aik din tere ghar wale bhi tujhe aakhri salaam keh kar waapas chale jayenge.
Aur us din tere saath sirf tere a'maal honge!
Ae Allah! Hamein maut se pehle sachchi tauba naseeb farma,
Hamari zubanon ki hifazat farma,
Aur jab hum is duniya se jayen
To hamein imaan ki haalat mein utha.
Aameen ya Rabbal Aalameen.""".split('\n')
subs = json.load(open('subs.json'))
assert len(R) == len(subs), (len(R), len(subs))
out = []
for (s, e, _, hl), line in zip(subs, R):
    words = line.split()
    groups, cur = [], []
    for w in words:
        if cur and (len(cur) >= 4 or len(' '.join(cur + [w])) > 24):
            groups.append(cur); cur = []
        cur.append(w)
    if cur: groups.append(cur)
    # time per word ~ proportional to letters (+2 for rhythm)
    wl = [len(w) + 2 for w in words]
    tot = sum(wl); span = (e - s) * 0.97
    t = s; times = []
    for w, l in zip(words, wl):
        times.append(t); t += span * l / tot
    i = 0
    for g in groups:
        n = len(g)
        gs = times[i]; ge = times[i + n] if i + n < len(words) else e
        out.append([round(gs, 2), round(ge, 2), g, [round(x, 2) for x in times[i:i + n]], hl])
        i += n
json.dump(out, open('roman.json', 'w'), ensure_ascii=False)
print(len(out))
