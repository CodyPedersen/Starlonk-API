#Starlink API

Epic
    - Implement calculations of location
        1. On-demand location calculations (DONE)
        2. Batch calculations (Data engineering)
            - Refresh at 5 second intervals
            - Pull from database of pre-calculated values
    - Implement other satellite sources (NOAA, Military, Weather)

Features: 
    - Move API auth for refresh to header (DONE)

Backlog
    - Include latitude/longitude