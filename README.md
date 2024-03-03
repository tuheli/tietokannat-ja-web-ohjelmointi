# Tietokannat ja web ohjelmointi

### Sovelluksen aihe ja ominaisuudet

Projektin aihe on kurssin valmiista aiheista valittu opetussovellus.

Ohjelman kuvaus:

Sovelluksen avulla voidaan järjestää verkkokursseja, joissa on tekstimateriaalia ja automaattisesti tarkastettavia tehtäviä. Jokainen käyttäjä on opettaja tai opiskelija.

Sovelluksen ominaisuuksia:

- Käyttäjä voi kirjautua sisään ja ulos sekä luoda uuden tunnuksen.
- Opiskelija näkee listan kursseista ja voi liittyä kurssille.
- Opiskelija voi lukea kurssin tekstimateriaalia sekä ratkoa kurssin tehtäviä.
- Opiskelija pystyy näkemään tilaston, mitkä kurssin tehtävät hän on ratkonut.
- Opettaja pystyy luomaan uuden kurssin, muuttamaan olemassa olevaa kurssia ja poistamaan kurssin.
- Opettaja pystyy lisäämään kurssille tekstimateriaalia ja tehtäviä. Tehtävä voi olla ainakin monivalinta tai tekstikenttä, johon tulee kirjoittaa oikea vastaus.
- Opettaja pystyy näkemään kurssistaan tilaston, keitä opiskelijoita on kurssilla ja mitkä kurssin tehtävät kukin on ratkonut.

### Sovelluksen käynnistysohjeet

Saat sovelluksen käyntiin [kurssisivulta](https://hy-tsoha.github.io/materiaali/aikataulu/) löytyvien ohjeiden mukaisesti:

- Kloonaa repositorio omalle koneellesi ja siirry sen juurikansioon.
- Luo kansioon .env-tiedosto ja määritä sen sisältö seuraavanlaiseksi:
  DATABASE_URL=tietokannan-paikallinen-osoite. Esimerkiksi postgresql:///user.
  SECRET_KEY=salainen-avain. Mikä tahansa merkkijono kelpaa.
- Aktivoi virtuaaliympäristö ja asenna sovelluksen riippuvuudet komennoilla: python3 -m venv venv, source venv/bin/activate ja pip install -r ./requirements.txt.
- Määritä tietokannan skeema komennolla: psql < schema.sql.
- Voit käynnistää sovelluksen komennolla flask run.
