import pytest
import pandas as pd
from chart_genius_mcp.server import ChartGeniusServer

@pytest.mark.asyncio
async def test_plotly_histogram_area_box_violin_bubble():
    server = ChartGeniusServer()
    df = pd.DataFrame({
        'x': [0,1,2,3,4,5,6,7,8,9],
        'y': [1,3,2,5,4,6,5,7,6,8],
        'g': ['A','A','B','B','A','A','B','B','A','A'],
        's': [10,20,15,25,18,22,19,30,17,24]
    })
    data = {"columns": df.columns.tolist(), "rows": df.to_dict('records')}

    # histogram
    r1 = await server._generate_chart(data=data, chart_type='histogram', engine='plotly', format='json')
    assert r1['success'] and r1['format'] == 'json'

    # area
    r2 = await server._generate_chart(data=data, chart_type='area', engine='plotly', format='json')
    assert r2['success'] and r2['format'] == 'json'

    # box
    r3 = await server._generate_chart(data=data, chart_type='box', engine='plotly', format='json')
    assert r3['success'] and r3['format'] == 'json'

    # violin
    r4 = await server._generate_chart(data=data, chart_type='violin', engine='plotly', format='json')
    assert r4['success'] and r4['format'] == 'json'

    # bubble (uses x,y,s)
    r5 = await server._generate_chart(data=data, chart_type='bubble', engine='plotly', format='json')
    assert r5['success'] and r5['format'] == 'json' 