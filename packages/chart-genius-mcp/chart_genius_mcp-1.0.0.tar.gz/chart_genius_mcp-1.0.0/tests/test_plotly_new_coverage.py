import pytest
import pandas as pd
from chart_genius_mcp.server import ChartGeniusServer

@pytest.mark.asyncio
async def test_treemap_sunburst_funnel_waterfall_radar_sankey_choropleth():
    server = ChartGeniusServer()

    # treemap/sunburst/funnel/waterfall
    df_cat = pd.DataFrame({
        'cat': ['A','A','B','B'],
        'val': [10,20,15,5]
    })
    data_cat = {"columns": df_cat.columns.tolist(), "rows": df_cat.to_dict('records')}

    r1 = await server._generate_chart(data=data_cat, chart_type='treemap', engine='plotly', format='json')
    assert r1['success']
    r2 = await server._generate_chart(data=data_cat, chart_type='sunburst', engine='plotly', format='json')
    assert r2['success']
    r3 = await server._generate_chart(data=data_cat, chart_type='funnel', engine='plotly', format='json')
    assert r3['success']
    df_w = pd.DataFrame({'step': ['Start','A','B','C'], 'amount': [100, -20, 15, -10]})
    data_w = {"columns": df_w.columns.tolist(), "rows": df_w.to_dict('records')}
    r4 = await server._generate_chart(data=data_w, chart_type='waterfall', engine='plotly', format='json')
    assert r4['success']

    # radar with explicit theta/r
    df_r = pd.DataFrame({'theta': ['m1','m2','m3'], 'r': [1,2,3]})
    data_r = {"columns": df_r.columns.tolist(), "rows": df_r.to_dict('records')}
    r5 = await server._generate_chart(data=data_r, chart_type='radar', engine='plotly', format='json')
    assert r5['success']

    # sankey
    df_s = pd.DataFrame({'source': ['A','A','B'], 'target': ['B','C','C'], 'value': [5,3,2]})
    data_s = {"columns": df_s.columns.tolist(), "rows": df_s.to_dict('records')}
    r6 = await server._generate_chart(data=data_s, chart_type='sankey', engine='plotly', format='json')
    assert r6['success']

    # choropleth with ISO-3 codes
    df_c = pd.DataFrame({'iso_alpha': ['USA','CAN','MEX'], 'metric': [100,80,60]})
    data_c = {"columns": df_c.columns.tolist(), "rows": df_c.to_dict('records')}
    r7 = await server._generate_chart(data=data_c, chart_type='choropleth', engine='plotly', format='json')
    assert r7['success'] 