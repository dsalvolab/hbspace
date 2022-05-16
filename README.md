# hbspace: Health Behavior in Space

## Purpose
Most geospatial indicators of built and food environment exposures are static (e.g., buffer-based GIS measures), and thus, are prone to the Uncertain Geographic Context Problem (UGCoP). Some physical activity and dietary behavior researchers have begun collecting time-matched GPS and accelerometry data to overcome this issue. However, processing and analyzing these data in a way that yields meaningful insights for answering health and place questions remains challenging. We aimed to develop an open-source code that integrates Geographic Positioning Systems (GPS) and accelerometer monitor data for obesity-related behavior research.

## Methods
We developed an open-source, Python code that integrates QTravel BT-10000 GPS and GT3X-wBT Actigraph device data via temporal matching. We implemented a series of rules to generate analytic datasets including variables about locations visited, trips between locations (distance, duration, travel mode), and spatiotemporally matched physical activity intensity categories. Output files include datasets at the following levels: 1) participant-level, 2) trip-level, 3) location-level, 4) visit-level, 5) fix-level (coordinates detected by the GPS monitor every 15 seconds). 

## References

Deborah Salvo, Alexandra van den Berg, Deanna Hoelscher, Alejandra Jauregui, Kathryn Janda, Kevin Lanza, Umberto Villa. *Integrating Geographic Positioning Systems and accelerometer monitor data for assessing the spatiotemporal patterns of health behaviors.* 21st Meeting of the International Society of Behavioral Nutrition and Physical Activity (ISBNPA), Phoenix, AZ, USA, MAy 2022.
