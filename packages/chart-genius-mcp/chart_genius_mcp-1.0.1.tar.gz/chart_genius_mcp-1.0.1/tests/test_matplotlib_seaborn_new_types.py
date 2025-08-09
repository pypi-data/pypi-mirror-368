import pytest
import pandas as pd
from chart_genius_mcp.server import ChartGeniusServer

@pytest.mark.asyncio
async def test_matplotlib_hist_area_box_violin_bubble():
    server = ChartGeniusServer()
    df = pd.DataFrame({'x':[0,1,2,3,4], 'y':[1,3,2,5,4], 'g':['A','A','B','B','A'], 's':[10,20,15,25,18]})
    data = {"columns": df.columns.tolist(), "rows": df.to_dict('records')}

    for t in ['histogram','area','box','violin','bubble']:
        r = await server._generate_chart(data=data, chart_type=t, engine='matplotlib', format='png')
        assert r['success'] and r['format'] == 'png' and r['content_type'] == 'image/png'

@pytest.mark.asyncio
async def test_seaborn_hist_area_box_violin_bubble():
    server = ChartGeniusServer()
    df = pd.DataFrame({'x':[0,1,2,3,4], 'y':[1,3,2,5,4], 'g':['A','A','B','B','A'], 's':[10,20,15,25,18]})
    data = {"columns": df.columns.tolist(), "rows": df.to_dict('records')}

    for t in ['histogram','area','box','violin','bubble']:
        r = await server._generate_chart(data=data, chart_type=t, engine='seaborn', format='png')
        assert r['success'] and r['format'] == 'png' and r['content_type'] == 'image/png' 