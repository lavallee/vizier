---
axes:
- chart_types:
  - Diverging bar
  - Diverging stacked bar
  - Spine chart
  - Surplus/deficit filled line
  description: Emphasise variations (+/-) from a fixed reference point. Typically
    the reference point is zero but it can also be a target or a long-term average.
    Can also be used to show sentiment (positive/neutral/negative). *Example FT uses:*
    Trade surplus/deficit, climate change
  name: Deviation
- chart_types:
  - Scatterplot
  - Line + Column
  - Connected scatterplot
  - Bubble
  - XY heatmap
  description: Show the relationship between two or more variables. Be mindful that,
    unless you tell them otherwise, many readers will assume the relationships you
    show them to be causal (i.e. one causes the other). *Example FT uses:* Inflation
    & unemployment, income & life expectancy
  name: Correlation
- chart_types:
  - Ordered bar
  - Ordered column
  - Ordered proportional symbol
  - Dot strip plot
  - Slope
  - Lollipop chart
  description: Use where an item’s position in an ordered list is more important than
    its absolute or relative value. Don’t be afraid to highlight the points of interest.
    *Example FT uses:* Wealth, deprivation, league tables, constituency election results
  name: Ranking
- chart_types:
  - Histogram
  - Boxplot
  - Violin plot
  - Population pyramid
  - Dot strip plot
  - Dot plot
  - Barcode plot
  - Cumulative curve
  description: Show values in a dataset and how often they occur. The shape (or ‘skew’)
    of a distribution can be a memorable way of highlighting the lack of uniformity
    or equality in the data. *Example FT uses:* Income distribution, population (age/sex)
    distribution
  name: Distribution
- chart_types:
  - Line
  - Column
  - Line + column
  - Stock price
  - Slope
  - Area chart
  - Fan chart (projection)
  - Connected scatterplot
  - Calendar heatmap
  - Priestley timeline
  - Circle timeline
  - Seismogram
  description: Give emphasis to changing trends. These can be short (intra-day) movements
    or extended series traversing decades or centuries. Choosing the correct time
    period is important to provide suitable context for the reader. *Example FT uses:*
    Share price movements, economic time series
  name: Change over Time
- chart_types:
  - Stacked column
  - Proportional stacked bar
  - Pie
  - Donut
  - Treemap
  - Voronoi
  - Arc
  - Gridplot
  - Venn
  - Waterfall
  description: Show how a single entity can bebroken down into its component elements.
    If the reader’s interest issolely in the size of the components,consider a magnitude-type
    chartinstead. *Example FT uses:* Fiscal budgets, company structures,national election
    results
  name: Part-to-whole
- chart_types:
  - Column
  - Bar
  - Paired column
  - Paired bar
  - Proportional stacked bar
  - Proportional symbol
  - Isotype (pictogram)
  - Lollipop chart
  - Radar chart
  - Parallel coordinates
  description: Show size comparisons. These can berelative (just being able to seelarger/bigger)
    or absolute (need tosee fine differences). Usually theseshow a ‘counted’ number
    (for example, barrels, dollars or people) rather thana calculated rate or per
    cent. *Example FT uses:* Commodity production, marketcapitalisation
  name: Magnitude
- chart_types:
  - Basic choropleth (rate/ratio)
  - Proportional symbol (count/magnitde)
  - Flow map
  - Contour map
  - Equalised cartogram
  - Scaled cartogram (value)
  - Dot density
  - Heat map
  description: Used only when precise locations orgeographical patterns in data aremore
    important to the reader thananything else. *Example FT uses:* Locator maps, population
    density,natural resource locations, naturaldisaster risk/impact, catchment areas,
    variation in election results
  name: Spatial
- chart_types:
  - Sankey (aka river plot)
  - Waterfall
  - Chord
  - Network
  description: Show the reader volumes or intensity of movement between two or more
    states or conditions. These might belogical sequences or geographical locations.
    *Example FT uses:* Movement of funds, trade, migrants, lawsuits, information;
    relationship graphs.
  name: Flow
details:
  chart_families:
    Change over Time:
      description: Give emphasis to changing trends. These can be short (intra-day)
        movements or extended series traversing decades or centuries. Choosing the
        correct time period is important to provide suitable context for the reader.
        *Example FT uses:* Share price movements, economic time series
      types:
      - description: The standard way to show a changing time series. If data are
          irregular, consider markers to represent data points
        name: Line
      - description: Columns work well for showing change over time - but usually
          best with only one series of data at a time.
        name: Column
      - description: A good way of showing the relationship over time between an amount
          (columns) and a rate (line)
        name: Line + column
      - description: Usually focused on day-to-day activity, these charts show opening/closing
          and hi/low points of each day
        name: Stock price
      - description: Good for showing changing data as long as the data can be simplified
          into 2 or 3 points without missing a key part of story
        name: Slope
      - description: Use with care – these are good at showing changes to total, but
          seeing change in components can be very difficult
        name: Area chart
      - description: Use to show the uncertainty in future projections - usually this
          grows the further forward to projection
        name: Fan chart (projection)
      - description: A good way of showing changing data for two variables whenever
          there is a relatively clear pattern of progression.
        name: Connected scatterplot
      - description: A great way of showing temporal patterns (daily, weekly, monthly)
          – at the expense of showing precision in quantity.
        name: Calendar heatmap
      - description: Great when date and duration are key elements of the story in
          the data.
        name: Priestley timeline
      - description: Good for showing discrete values of varying size across multiple
          categories (eg earthquakes by contintent).
        name: Circle timeline
      - description: Another alternative to the circle timeline for showing series
          where there are big variations in the data.
        name: Seismogram
    Correlation:
      description: Show the relationship between two or more variables. Be mindful
        that, unless you tell them otherwise, many readers will assume the relationships
        you show them to be causal (i.e. one causes the other). *Example FT uses:*
        Inflation & unemployment, income & life expectancy
      types:
      - description: The standard way to show the relationship between two continuous
          variables, each of which has its own axis.
        name: Scatterplot
      - description: A good way of showing the relationship between an amount (columns)
          and a rate (line)
        name: Line + Column
      - description: Usually used to show how the relationship between two variables
          has changed over time.
        name: Connected scatterplot
      - description: Like a scatterplot, but adds additional detail by sizing the
          circles according to a third variable
        name: Bubble
      - description: A good way of showing the patterns between 2 categories of data,
          less good at showing fine differences in amounts.
        name: XY heatmap
    Deviation:
      description: Emphasise variations (+/-) from a fixed reference point. Typically
        the reference point is zero but it can also be a target or a long-term average.
        Can also be used to show sentiment (positive/neutral/negative). *Example FT
        uses:* Trade surplus/deficit, climate change
      types:
      - description: A simple standard bar chart that can handle both negative and
          positive magnitude values.
        name: Diverging bar
      - description: Perfect for presenting survey results which involve sentiment
          (eg disagree/neutral/agree).
        name: Diverging stacked bar
      - description: Splits a single value into 2 contrasting components (eg Male/Female)
        name: Spine chart
      - description: The shaded area of these charts allows a balance to be shown
          – either against a baseline or between two series.
        name: Surplus/deficit filled line
    Distribution:
      description: Show values in a dataset and how often they occur. The shape (or
        ‘skew’) of a distribution can be a memorable way of highlighting the lack
        of uniformity or equality in the data. *Example FT uses:* Income distribution,
        population (age/sex) distribution
      types:
      - description: The standard way to show a statistical distribution - keep the
          gaps between columns small to highlight the ‘shape’ of the data
        name: Histogram
      - description: Summarise multiple distributions by showing the median (centre)
          and range of the data
        name: Boxplot
      - description: Similar to a box plot but more effective with complex distributions
          (data that cannot be summarised with simple average).
        name: Violin plot
      - description: A standard way for showing the age and sex breakdown of a population
          distribution; effectively, back to back histograms.
        name: Population pyramid
      - description: Good for showing individual values in a distribution, can be
          a problem when too many dots have the same value.
        name: Dot strip plot
      - description: A simple way of showing the change or range (min/max) of data
          across multiple categories.
        name: Dot plot
      - description: Like dot strip plots, good for displaying all the data in a table,they
          work best when highlighting individual values.
        name: Barcode plot
      - description: 'A good way of showing how unequal a distribution is: y axis
          is always cumulative frequency, x axis is always a measure.'
        name: Cumulative curve
    Flow:
      description: Show the reader volumes or intensity of movement between two or
        more states or conditions. These might belogical sequences or geographical
        locations. *Example FT uses:* Movement of funds, trade, migrants, lawsuits,
        information; relationship graphs.
      types:
      - description: Shows changes in flows from one condition to at least one other;
          good for tracing the eventual outcome of a complex process.
        name: Sankey (aka river plot)
      - description: Designed to show the sequencing of data through a flow process,
          typically budgets. Can include +/- components.
        name: Waterfall
      - description: A complex but powerful diagram which can illustrate 2-way flows
          (and net winner) in a matrix.
        name: Chord
      - description: Used for showing the strength and inter-connectedness of relationships
          of varying types.
        name: Network
    Magnitude:
      description: Show size comparisons. These can berelative (just being able to
        seelarger/bigger) or absolute (need tosee fine differences). Usually theseshow
        a ‘counted’ number (for example, barrels, dollars or people) rather thana
        calculated rate or per cent. *Example FT uses:* Commodity production, marketcapitalisation
      types:
      - description: The standard way to compare the size of things. Must always start
          at 0 on the axis
        name: Column
      - description: See above. Good when the data are not time series and labels
          have long category names.
        name: Bar
      - description: As per standard column but allows for multiple series. Can become
          tricky to read with more than 2 series.
        name: Paired column
      - description: See above.
        name: Paired bar
      - description: A good way of showing the size and proportion of data at the
          same time – as long as the data are not too complicated.
        name: Proportional stacked bar
      - description: Use when there are big variations between values and/or seeing
          fine differences between data is not so important.
        name: Proportional symbol
      - description: Excellent solution in some instances – use only with whole numbers
          (do not slice off an arm to represent a decimal).
        name: Isotype (pictogram)
      - description: Lollipop charts draw more attention to the data value than standard
          bar/column – does not HAVE to start at zero (but preferable).
        name: Lollipop chart
      - description: A space-efficient way of showing value pf multiple variables–
          but make sure they are organised in a way that makes sense to reader.
        name: Radar chart
      - description: An alternative to radar charts – again, the arrngement of the
          variables is important. Usually benefits from highlighting values.
        name: Parallel coordinates
    Part-to-whole:
      description: Show how a single entity can bebroken down into its component elements.
        If the reader’s interest issolely in the size of the components,consider a
        magnitude-type chartinstead. *Example FT uses:* Fiscal budgets, company structures,national
        election results
      types:
      - description: A simple way of showing part-to-whole relationships but can be
          difficult to read with more than a few components.
        name: Stacked column
      - description: A good way of showing the size and proportion of data at the
          same time – as long as the data are not too complicated.
        name: Proportional stacked bar
      - description: A common way of showing part-to-whole data – but be aware that
          it’s difficult to accurately compare the size of the segments.
        name: Pie
      - description: Similar to a pie chart – but the centre can be a good way of
          making space to include more information about the data (eg. total)
        name: Donut
      - description: Use for hierarchical part-to-whole relationships; can be difficult
          to read when there are many small segments.
        name: Treemap
      - description: A way of turning points into areas – any point within each area
          is closer to the central point than any other centroid.
        name: Voronoi
      - description: A hemicycle, often used for visualising political results in
          parliaments.
        name: Arc
      - description: Good for showing % information, they work best when used on whole
          numbers and work well in multiple layout form.
        name: Gridplot
      - description: Generally only used for schematic representation
        name: Venn
      - description: Can be useful for showing part-to-whole relationships where some
          of the components are negative.
        name: Waterfall
    Ranking:
      description: Use where an item’s position in an ordered list is more important
        than its absolute or relative value. Don’t be afraid to highlight the points
        of interest. *Example FT uses:* Wealth, deprivation, league tables, constituency
        election results
      types:
      - description: Standard bar charts display the ranks of values much more easily
          when sorted into order
        name: Ordered bar
      - description: See above.
        name: Ordered column
      - description: Use when there are big variations between values and/or seeing
          fine differences between data is not so important.
        name: Ordered proportional symbol
      - description: Dots placed in order on a strip are a space-efficient method
          of laying out ranks across multiple categories.
        name: Dot strip plot
      - description: Perfect for showing how ranks have changed over time or vary
          between categories.
        name: Slope
      - description: Lollipops draw more attention to the data value than standard
          bar/column and can also show rank and value effectively.
        name: Lollipop chart
    Spatial:
      description: Used only when precise locations orgeographical patterns in data
        aremore important to the reader thananything else. *Example FT uses:* Locator
        maps, population density,natural resource locations, naturaldisaster risk/impact,
        catchment areas, variation in election results
      types:
      - description: The standard approach for putting data on a map – should always
          be rates rather than totals and use a sensible base geography
        name: Basic choropleth (rate/ratio)
      - description: Use for totals rather than rates – be wary that small differences
          in data will be hard to see.
        name: Proportional symbol (count/magnitde)
      - description: For showing unambiguous movement across a map.
        name: Flow map
      - description: For showing areas of equal value on a map. Can use deviation
          colour schemes for showing +/- values
        name: Contour map
      - description: Converting each unit on a map to a regular and equally-sized
          shape – good for representing voting regions with equal value.
        name: Equalised cartogram
      - description: Stretching and shrinking a map so that each area is sized according
          to a particular value.
        name: Scaled cartogram (value)
      - description: Used to show the location of individual events/locations – make
          sure to annotate any patterns the reader should see.
        name: Dot density
      - description: Grid-based data values mapped with an intensity colour scale.
          As choropleth map – but not snapped to an admin/political unit.
        name: Heat map
  origin: Financial-Times/chart-doctor/visual-vocabulary
fetched_at: '2026-04-18T19:24:50.942065Z'
id: ft-visual-vocabulary
source: ft-vocab
tags:
- rubric
- chart-selection
- ft
- canonical
title: FT Visual Vocabulary
type: rubric
url: https://github.com/Financial-Times/chart-doctor/tree/main/visual-vocabulary
---

FT's Visual Vocabulary is a poster + web reference used by the FT Visual Journalism Team to pick chart forms by the comparison being made. Nine chart families, each with a family of sub-types. Selection starts by identifying the comparison (deviation? correlation? part-to-whole?) and narrows to a specific type from there.

## Families

### Deviation

Emphasise variations (+/-) from a fixed reference point. Typically the reference point is zero but it can also be a target or a long-term average. Can also be used to show sentiment (positive/neutral/negative). *Example FT uses:* Trade surplus/deficit, climate change

- **Diverging bar**: A simple standard bar chart that can handle both negative and positive magnitude values.
- **Diverging stacked bar**: Perfect for presenting survey results which involve sentiment (eg disagree/neutral/agree).
- **Spine chart**: Splits a single value into 2 contrasting components (eg Male/Female)
- **Surplus/deficit filled line**: The shaded area of these charts allows a balance to be shown – either against a baseline or between two series.

### Correlation

Show the relationship between two or more variables. Be mindful that, unless you tell them otherwise, many readers will assume the relationships you show them to be causal (i.e. one causes the other). *Example FT uses:* Inflation & unemployment, income & life expectancy

- **Scatterplot**: The standard way to show the relationship between two continuous variables, each of which has its own axis.
- **Line + Column**: A good way of showing the relationship between an amount (columns) and a rate (line)
- **Connected scatterplot**: Usually used to show how the relationship between two variables has changed over time.
- **Bubble**: Like a scatterplot, but adds additional detail by sizing the circles according to a third variable
- **XY heatmap**: A good way of showing the patterns between 2 categories of data, less good at showing fine differences in amounts.

### Ranking

Use where an item’s position in an ordered list is more important than its absolute or relative value. Don’t be afraid to highlight the points of interest. *Example FT uses:* Wealth, deprivation, league tables, constituency election results

- **Ordered bar**: Standard bar charts display the ranks of values much more easily when sorted into order
- **Ordered column**: See above.
- **Ordered proportional symbol**: Use when there are big variations between values and/or seeing fine differences between data is not so important.
- **Dot strip plot**: Dots placed in order on a strip are a space-efficient method of laying out ranks across multiple categories.
- **Slope**: Perfect for showing how ranks have changed over time or vary between categories.
- **Lollipop chart**: Lollipops draw more attention to the data value than standard bar/column and can also show rank and value effectively.

### Distribution

Show values in a dataset and how often they occur. The shape (or ‘skew’) of a distribution can be a memorable way of highlighting the lack of uniformity or equality in the data. *Example FT uses:* Income distribution, population (age/sex) distribution

- **Histogram**: The standard way to show a statistical distribution - keep the gaps between columns small to highlight the ‘shape’ of the data
- **Boxplot**: Summarise multiple distributions by showing the median (centre) and range of the data
- **Violin plot**: Similar to a box plot but more effective with complex distributions (data that cannot be summarised with simple average).
- **Population pyramid**: A standard way for showing the age and sex breakdown of a population distribution; effectively, back to back histograms.
- **Dot strip plot**: Good for showing individual values in a distribution, can be a problem when too many dots have the same value.
- **Dot plot**: A simple way of showing the change or range (min/max) of data across multiple categories.
- **Barcode plot**: Like dot strip plots, good for displaying all the data in a table,they work best when highlighting individual values.
- **Cumulative curve**: A good way of showing how unequal a distribution is: y axis is always cumulative frequency, x axis is always a measure.

### Change over Time

Give emphasis to changing trends. These can be short (intra-day) movements or extended series traversing decades or centuries. Choosing the correct time period is important to provide suitable context for the reader. *Example FT uses:* Share price movements, economic time series

- **Line**: The standard way to show a changing time series. If data are irregular, consider markers to represent data points
- **Column**: Columns work well for showing change over time - but usually best with only one series of data at a time.
- **Line + column**: A good way of showing the relationship over time between an amount (columns) and a rate (line)
- **Stock price**: Usually focused on day-to-day activity, these charts show opening/closing and hi/low points of each day
- **Slope**: Good for showing changing data as long as the data can be simplified into 2 or 3 points without missing a key part of story
- **Area chart**: Use with care – these are good at showing changes to total, but seeing change in components can be very difficult
- **Fan chart (projection)**: Use to show the uncertainty in future projections - usually this grows the further forward to projection
- **Connected scatterplot**: A good way of showing changing data for two variables whenever there is a relatively clear pattern of progression.
- **Calendar heatmap**: A great way of showing temporal patterns (daily, weekly, monthly) – at the expense of showing precision in quantity.
- **Priestley timeline**: Great when date and duration are key elements of the story in the data.
- **Circle timeline**: Good for showing discrete values of varying size across multiple categories (eg earthquakes by contintent).
- **Seismogram**: Another alternative to the circle timeline for showing series where there are big variations in the data.

### Part-to-whole

Show how a single entity can bebroken down into its component elements. If the reader’s interest issolely in the size of the components,consider a magnitude-type chartinstead. *Example FT uses:* Fiscal budgets, company structures,national election results

- **Stacked column**: A simple way of showing part-to-whole relationships but can be difficult to read with more than a few components.
- **Proportional stacked bar**: A good way of showing the size and proportion of data at the same time – as long as the data are not too complicated.
- **Pie**: A common way of showing part-to-whole data – but be aware that it’s difficult to accurately compare the size of the segments.
- **Donut**: Similar to a pie chart – but the centre can be a good way of making space to include more information about the data (eg. total)
- **Treemap**: Use for hierarchical part-to-whole relationships; can be difficult to read when there are many small segments.
- **Voronoi**: A way of turning points into areas – any point within each area is closer to the central point than any other centroid.
- **Arc**: A hemicycle, often used for visualising political results in parliaments.
- **Gridplot**: Good for showing % information, they work best when used on whole numbers and work well in multiple layout form.
- **Venn**: Generally only used for schematic representation
- **Waterfall**: Can be useful for showing part-to-whole relationships where some of the components are negative.

### Magnitude

Show size comparisons. These can berelative (just being able to seelarger/bigger) or absolute (need tosee fine differences). Usually theseshow a ‘counted’ number (for example, barrels, dollars or people) rather thana calculated rate or per cent. *Example FT uses:* Commodity production, marketcapitalisation

- **Column**: The standard way to compare the size of things. Must always start at 0 on the axis
- **Bar**: See above. Good when the data are not time series and labels have long category names.
- **Paired column**: As per standard column but allows for multiple series. Can become tricky to read with more than 2 series.
- **Paired bar**: See above.
- **Proportional stacked bar**: A good way of showing the size and proportion of data at the same time – as long as the data are not too complicated.
- **Proportional symbol**: Use when there are big variations between values and/or seeing fine differences between data is not so important.
- **Isotype (pictogram)**: Excellent solution in some instances – use only with whole numbers (do not slice off an arm to represent a decimal).
- **Lollipop chart**: Lollipop charts draw more attention to the data value than standard bar/column – does not HAVE to start at zero (but preferable).
- **Radar chart**: A space-efficient way of showing value pf multiple variables– but make sure they are organised in a way that makes sense to reader.
- **Parallel coordinates**: An alternative to radar charts – again, the arrngement of the variables is important. Usually benefits from highlighting values.

### Spatial

Used only when precise locations orgeographical patterns in data aremore important to the reader thananything else. *Example FT uses:* Locator maps, population density,natural resource locations, naturaldisaster risk/impact, catchment areas, variation in election results

- **Basic choropleth (rate/ratio)**: The standard approach for putting data on a map – should always be rates rather than totals and use a sensible base geography
- **Proportional symbol (count/magnitde)**: Use for totals rather than rates – be wary that small differences in data will be hard to see.
- **Flow map**: For showing unambiguous movement across a map.
- **Contour map**: For showing areas of equal value on a map. Can use deviation colour schemes for showing +/- values
- **Equalised cartogram**: Converting each unit on a map to a regular and equally-sized shape – good for representing voting regions with equal value.
- **Scaled cartogram (value)**: Stretching and shrinking a map so that each area is sized according to a particular value.
- **Dot density**: Used to show the location of individual events/locations – make sure to annotate any patterns the reader should see.
- **Heat map**: Grid-based data values mapped with an intensity colour scale. As choropleth map – but not snapped to an admin/political unit.

### Flow

Show the reader volumes or intensity of movement between two or more states or conditions. These might belogical sequences or geographical locations. *Example FT uses:* Movement of funds, trade, migrants, lawsuits, information; relationship graphs.

- **Sankey (aka river plot)**: Shows changes in flows from one condition to at least one other; good for tracing the eventual outcome of a complex process.
- **Waterfall**: Designed to show the sequencing of data through a flow process, typically budgets. Can include +/- components.
- **Chord**: A complex but powerful diagram which can illustrate 2-way flows (and net winner) in a matrix.
- **Network**: Used for showing the strength and inter-connectedness of relationships of varying types.
