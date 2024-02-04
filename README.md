# tietokannat-ja-web-ohjelmointi

flask app university course project

### Sovelluksen aihe ja ominaisuudet

Projektin aihe on kurssin valmiista aiheista valittu opetussovellus.

Ohjelman kuvaus sellaisena kuin se on [kurssisivulla](https://hy-tsoha.github.io/materiaali/aiheen_valinta/) esitetty:

"Sovelluksen avulla voidaan järjestää verkkokursseja, joissa on tekstimateriaalia ja automaattisesti tarkastettavia tehtäviä. Jokainen käyttäjä on opettaja tai opiskelija.

Sovelluksen ominaisuuksia:

- Käyttäjä voi kirjautua sisään ja ulos sekä luoda uuden tunnuksen.
- Opiskelija näkee listan kursseista ja voi liittyä kurssille.
- Opiskelija voi lukea kurssin tekstimateriaalia sekä ratkoa kurssin tehtäviä.
- Opiskelija pystyy näkemään tilaston, mitkä kurssin tehtävät hän on ratkonut.
- Opettaja pystyy luomaan uuden kurssin, muuttamaan olemassa olevaa kurssia ja poistamaan kurssin.
- Opettaja pystyy lisäämään kurssille tekstimateriaalia ja tehtäviä. Tehtävä voi olla ainakin monivalinta tai tekstikenttä, johon tulee kirjoittaa oikea vastaus.
- Opettaja pystyy näkemään kurssistaan tilaston, keitä opiskelijoita on kurssilla ja mitkä kurssin tehtävät kukin on ratkonut."

### Sovelluksen kehityksen tilanne

Sovelluksen kehityksen tilanne (yllä olevasta kuvauksesta puuttuvat ominaisuudet):

- Opiskelija voi ratkoa kurssin tehtäviä.
- Opiskelija pystyy näkemään tilaston, mitkä kurssin tehtävät hän on ratkonut.
- Opettaja pystyy muuttamaan olemassa olevaa kurssia (voi kuitenkin lisätä tehtäviä) ja poistamaan kurssin.
- Opettaja pystyy näkemään kurssistaan tilaston, keitä opiskelijoita on kurssilla ja mitkä kurssin tehtävät kukin on ratkonut.

Ominaisuuksista on toteutettu 9 / 15.

### Sovelluksen käynnistysohjeet

Saat sovelluksen käyntiin [kurssisivulta](https://hy-tsoha.github.io/materiaali/aikataulu/) löytyvien ohjeiden mukaisesti:

- "Kloonaa tämä repositorio omalle koneellesi ja siirry sen juurikansioon.
- Luo kansioon .env-tiedosto ja määritä sen sisältö seuraavanlaiseksi:
  DATABASE_URL=tietokannan-paikallinen-osoite (oma lisäys: esim. postgresql:///user, sitaatista poistettu <> merkit)
  SECRET_KEY=salainen-avain (oma lisäys: kirjoita vaan jokin merkkijono, sitaatista poistettu <> merkit)
- Seuraavaksi aktivoi virtuaaliympäristö ja asenna sovelluksen riippuvuudet komennoilla: python3 -m venv venv, source venv/bin/activate ja pip install -r ./requirements.txt
- Määritä vielä tietokannan skeema komennolla:
  psql < schema.sql (oma lisäys: tarvit tietenkin postgresin koneellesi. Itse käytin macilla appia https://postgresapp.com/. Jos sinulla on toinen käyttöjärjestelmä ks. https://www.postgresql.org/)
- Nyt voit käynnistää sovelluksen komennolla flask run"
