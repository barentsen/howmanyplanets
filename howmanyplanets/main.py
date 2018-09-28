"""
TODO
- How to establish a callback policy for the sliders.
- Mark Solar System planets?
- The term "jupiter-size" can be confusing
- Add Lato font to css.
"""
import numpy as np

from bokeh.core.properties import field
from bokeh.io import curdoc
from bokeh.layouts import layout, widgetbox
from bokeh.models import (ColumnDataSource, HoverTool, FixedTicker, BasicTickFormatter,
                          RangeSlider, Label, CategoricalColorMapper, Div, Markup)
from bokeh.plotting import figure

from howmanyplanets import prepare_planet_data, occurence_rate

RADIUS_RANGE = (0.3, 30)
PERIOD_RANGE = (0.1, 2000)


keplerdf = prepare_planet_data()
keplerdf.loc[:, 'circlesize'] = 2 + keplerdf['fpl_rade']
data = keplerdf.to_dict('series')

source = ColumnDataSource(data=data)
source_gray = ColumnDataSource(data=data)

solsys_planets = ['Mercury', 'Venus', 'Earth', 'Mars', 'Jupiter', 'Saturn', 'Uranus', 'Neptune']
solsys_radii = [0.382, 0.949, 1, 0.532, 11.209, 9.44, 4.007, 3.883]
solsys_periods = [0.24, 0.62, 1, 1.88, 11.86, 29.46, 84.01, 164.8]
solsys_data = {'planets': solsys_planets,
               'radii': solsys_radii,
               'periods': 365 * np.array(solsys_periods),
               'circlesize': 2 + np.array(solsys_radii)}
source_solsys = ColumnDataSource(data=solsys_data)


plot = figure(x_range=PERIOD_RANGE, y_range=RADIUS_RANGE,
              x_axis_type="log", y_axis_type="log",
              plot_width=600, plot_height=450)

plot.xaxis.ticker = FixedTicker(ticks=[0.1, 1, 10, 100, 365, 2000])
plot.xaxis.formatter = BasicTickFormatter()
plot.xaxis.axis_label = "Orbital period (days)"

plot.yaxis.ticker = FixedTicker(ticks=[0.3, 0.5, 1, 2, 4, 10, 30])
plot.yaxis.formatter = BasicTickFormatter()
plot.yaxis.axis_label = "Planet size (relative to Earth)"

color_mapper = CategoricalColorMapper(palette=['#3498db', '#2ecc71', '#f1c40f', '#e74c3c'],
                                      factors=['Earth-size', 'Super-Earth-size', 'Neptune-size', 'Jupiter-size'])

circles_gray = plot.circle(
    x='fpl_orbper',
    y='fpl_rade',
    size='circlesize',
    source=source_gray,
    fill_color='#bbbbbb',
    fill_alpha=0.8,
    line_color='#000000',
    line_width=0.5,
    line_alpha=0.5,
)

circles = plot.circle(
    x='fpl_orbper',
    y='fpl_rade',
    size='circlesize',
    source=source,
    fill_color={'field': 'category', 'transform': color_mapper},
    fill_alpha=0.8,
    line_color='#000000',
    line_width=0.5,
    line_alpha=0.5,
    legend=field('category'),
)

circles_solsys = plot.circle(
    x='periods',
    y='radii',
    size='circlesize',
    source=source_solsys,
    fill_color='#ffffff',
    line_color='#000000',
    line_width=0.5,
    line_alpha=0.5,
)

plot.add_tools(HoverTool(tooltips="@fpl_name", show_arrow=False, point_policy='follow_mouse'))


div_planets_pre = Div(text="NASA's Kepler mission has discovered",
                      css_classes=['keptxt'])
div_planets = Div(text="", css_classes=['kepstat'])
div_planets_post = Div(text="around other stars so far.", css_classes=['keptxt'])

div_occurence_pre = Div(text="", css_classes=['keptxt', 'kepbr'])
div_occurence = Div(text="", css_classes=['kepstat'])
div_occurence_post = Div(text="", css_classes=['keptxt'])

div_count_pre = Div(css_classes=['keptxt', 'kepbr'])
div_count = Div(css_classes=['kepstat'])
div_count_post = Div(text="", css_classes=['keptxt'])

div_period_pre = Div(text="The planets have orbital periods between",
                     css_classes=['keptxt', 'kepbr'])
div_period = Div(text="", css_classes=['kepstat', 'period-range'])
div_radius_pre = Div(text="and sizes between",
                     css_classes=['keptxt'])
div_radius = Div(text="", css_classes=['kepstat'])
div_radius_post = Div(text="Use the sliders to narrow down the ranges.",
                      css_classes=['keptxt'])


def fmt(number):
    if number < 100:
        return "{:.1f}".format(number)
    return "{:.0f}".format(number)


def update_limits(attr, old, new):
    r1, r2 = radius_slider.value
    min_radius, max_radius = 10**r1, 10**r2
    p1, p2 = period_slider.value
    min_period, max_period = 10**p1, 10**p2

    mask = (keplerdf.fpl_rade >= min_radius) & (keplerdf.fpl_rade <= max_radius) & \
           (keplerdf.fpl_orbper >= min_period) & (keplerdf.fpl_orbper <= max_period)
    source.data = keplerdf[mask].to_dict('series')
    n_planets = mask.sum()

    div_planets.text = "{} planets<sup>*</sup>".format(n_planets)
    div_period.text = fmt(min_period) + " – " + fmt(max_period) + " days"
    div_radius.text = "{:.1f} – {:.1f} Earth radii.".format(min_radius, max_radius)

    if n_planets < 3:
        div_occurence_pre.text = 'But we'
        div_occurence.text = 'need more data'
        div_occurence_post.text = 'to understand how common they are.'
        div_count_pre.text = ''
        div_count.text = ''
        div_count_post.text = ''
    else:
        eta = occurence_rate(rmin=min_radius, rmax=max_radius, pmin=min_period, pmax=max_period)
        div_occurence_pre.text = "On average, we think there are"
        div_occurence.text = "{:.2f} planets per Sun<sup>†</sup>".format(eta)
        div_occurence_post.text = "of the types discovered by Kepler."
        div_count_pre.text = 'This implies the presence of at least'
        div_count.text = "{:.0f} billion planets<sup>‡</sup>".format(20*eta)
        div_count_post.text = 'across our Galaxy.'


period_slider = RangeSlider(start=np.log10(PERIOD_RANGE[0]), end=np.log10(PERIOD_RANGE[1]),
                            value=(np.log10(PERIOD_RANGE[0]), np.log10(PERIOD_RANGE[1])),
                            step=.01, title=None, show_value=False,
                            css_classes=['period-slider'])
period_slider.on_change('value', update_limits)

radius_slider = RangeSlider(start=np.log10(RADIUS_RANGE[0]), end=np.log10(RADIUS_RANGE[1]),
                            value=(np.log10(RADIUS_RANGE[0]), np.log10(RADIUS_RANGE[1])),
                            step=.01, title=None, show_value=False,
                            callback_policy='mouseup',
                            css_classes=['radius-slider'])
radius_slider.on_change('value', update_limits)


callback_id = None


layout = layout([
    [widgetbox([div_planets_pre, div_planets, div_planets_post,
                div_occurence_pre, div_occurence, div_occurence_post,
                div_count_pre, div_count, div_count_post,
                div_period_pre, div_period, period_slider,
                div_radius_pre, div_radius, radius_slider, div_radius_post],
               width=287, css_classes=['kepwidgets']),
     plot],
],)

update_limits(None, None, None)  # Initialize the numbers
curdoc().add_root(layout)
