"""
Deterministic unit tests for the DRAMeXchange memory-quote parser.

Uses a static HTML snippet (mirroring the real page structure) so the test
does not hit the network and locks in extraction of real prices — including
the DDR3 row, which earlier versions of the ingest pipeline dropped.
"""
from app.services.memory_quote_parser import classify_product, parse_quotes_from_html

SAMPLE_HTML = """
<html><body>
<table>
  <tr><th>Item</th><th>Daily High</th><th>Daily Low</th><th>Session High</th>
      <th>Session Low</th><th>Session Average</th><th>Change</th><th>History</th></tr>
  <tr><td>DDR5 16Gb (2Gx8) 4800/5600</td><td>59.50</td><td>31.00</td><td>59.50</td>
      <td>31.00</td><td>46.500</td><td>0.72 %</td><td></td></tr>
  <tr><td>DDR4 16Gb (2Gx8) 3200</td><td>85.00</td><td>38.00</td><td>85.00</td>
      <td>38.00</td><td>70.634</td><td>1.27 %</td><td></td></tr>
  <tr><td>DDR3 4Gb 512Mx8 1600/1866</td><td>16.50</td><td>6.60</td><td>16.50</td>
      <td>6.60</td><td>11.271</td><td>1.07 %</td><td></td></tr>
  <tr><td>DDR5 UDIMM 16GB 4800/5600</td><td>215.00</td><td>200.00</td><td>215.00</td>
      <td>200.00</td><td>209.000</td><td>0.00 %</td><td></td></tr>
  <tr><td>512Gb TLC</td><td>22.00</td><td>16.00</td><td>22.00</td>
      <td>16.00</td><td>20.431</td><td>-1.00 %</td><td></td></tr>
  <tr><td>MLC 64Gb 8GBx8</td><td>40.00</td><td>23.00</td><td>40.00</td>
      <td>23.00</td><td>28.182</td><td>6.17 %</td><td></td></tr>
  <tr><td>Some heading row that is not a price</td><td>foo</td></tr>
</table>
</body></html>
"""


def test_parses_real_prices_with_ddr3():
    quotes = parse_quotes_from_html(SAMPLE_HTML)
    by_product = {q["product"]: q for q in quotes}

    # DDR3 must be present with its real average + change (regression guard).
    assert "DDR3 4Gb 512Mx8 1600/1866" in by_product
    ddr3 = by_product["DDR3 4Gb 512Mx8 1600/1866"]
    assert ddr3["category"] == "DRAM"
    assert ddr3["price_type"] == "spot"
    assert ddr3["price_avg"] == 11.271
    assert ddr3["change_pct"] == 1.07

    # DDR5 spot + DDR4 spot carry real averages.
    assert by_product["DDR5 16Gb (2Gx8) 4800/5600"]["price_avg"] == 46.5
    assert by_product["DDR4 16Gb (2Gx8) 3200"]["change_pct"] == 1.27


def test_classification_buckets():
    assert classify_product("DDR5 UDIMM 16GB 4800/5600") == ("DRAM", "module")
    assert classify_product("DDR3 4Gb 512Mx8 1600/1866") == ("DRAM", "spot")
    assert classify_product("512Gb TLC") == ("NAND", "wafer")
    assert classify_product("MLC 64Gb 8GBx8") == ("NAND", "flash")
    assert classify_product("GDDR6 8Gb") == ("DRAM", "spot")


def test_non_price_rows_ignored():
    quotes = parse_quotes_from_html(SAMPLE_HTML)
    products = {q["product"] for q in quotes}
    assert "Some heading row that is not a price" not in products
    # 6 real priced rows in the sample.
    assert len(quotes) == 6
