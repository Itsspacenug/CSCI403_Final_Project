SET search_path TO group120807;

\COPY stations FROM '/Users/aaronnguyen/Documents/VS_Code/CSCI403/CSCI403_Final_Project/stations.csv' CSV HEADER;
\COPY oni FROM '/Users/aaronnguyen/Documents/VS_Code/CSCI403/CSCI403_Final_Project/Monthly_ONI.csv' CSV HEADER;
\COPY pdo FROM '/Users/aaronnguyen/Documents/VS_Code/CSCI403/CSCI403_Final_Project/PDO.csv' CSV HEADER;
\COPY snotel FROM '/Users/aaronnguyen/Documents/VS_Code/CSCI403/CSCI403_Final_Project/snotel_all_stations.csv' CSV HEADER;
\COPY streamflow FROM '/Users/aaronnguyen/Documents/VS_Code/CSCI403/CSCI403_Final_Project/streamflow.csv' CSV HEADER;
