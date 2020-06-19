![alt text](https://github.com/CleHou/COVID-19-Data-Analysis-Project/blob/master/99-Other/99.1-Logo/Logo2_100px.png)
# COVID-19 Data Analysis Project - 02 - Maps
This code is used to generate 3 maps : 
* The number of cases / death per day (time slider on the side) - only on a world scale
* The weekly increase in the daily number of cases or death - on a world scale, region scale (France) and states scale (US)
* The number of cases or death per capita - on a world scale, region scale (France) and states scale (US)

As for all the codes in the repository, if the `import_df_from_I()` function is used instead of `import_df_from_xlsx()`, the data is automaticaly updated.
For this code, the data is imported from [John Hopkins Univeristy](https://github.com/CSSEGISandData/COVID-19/tree/master/csse_covid_19_data/csse_covid_19_time_series), [OpenCOVID19 France GitHub repository](https://github.com/opencovid19-fr/data/blob/master/dist/chiffres-cles.csv), [Census.gov](https://www.census.gov/topics/population.html), [Santé Publique France](https://www.census.gov/topics/population.html), [DataNova](https://datanova.laposte.fr/explore/dataset/contours-geographiques-des-nouvelles-regions-metropole/export/), [INSEE](https://www.insee.fr/fr/statistiques/1893198), [United Nations](https://population.un.org/wpp/).

Examples of the output: 
![alt text](http://houzardc.fr/MapCases.png)
![alt text](https://houzardc.fr/wp-content/uploads/2020/05/Map_Relative_Death_Fra.png)
![alt text](https://houzardc.fr/wp-content/uploads/2020/05/Map_Relative_Cases_US.png)
