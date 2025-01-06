def get_airport_name_by_code(iata_code, airports_df):
    if airports_df is not None:
        result = airports_df.loc[airports_df['iata_code'].str.upper() == iata_code.upper(), 'airport_name']
        if not result.empty:
            return result.values[0]
    return "Unknown Airport"
