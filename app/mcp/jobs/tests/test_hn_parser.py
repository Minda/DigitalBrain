"""
Unit tests for HN HTML parsing helpers.
TC-S5, TC-S8
"""

from mcp_jobs.scrapers.hn import strip_html, parse_company, parse_title, parse_location


class TestStripHtml:
    def test_strips_p_tags(self):
        assert "hello" in strip_html("<p>hello</p>")

    def test_strips_br_tags(self):
        result = strip_html("line1<br>line2")
        assert "line1" in result
        assert "line2" in result
        assert "<br>" not in result

    def test_preserves_link_url(self):
        result = strip_html('<a href="https://example.com">Apply here</a>')
        assert "https://example.com" in result

    def test_link_text_equals_url_shows_just_url(self):
        result = strip_html('<a href="https://example.com">https://example.com</a>')
        assert result.count("https://example.com") == 1

    def test_link_with_different_text(self):
        result = strip_html('<a href="https://jobs.example.com">Apply here</a>')
        assert "Apply here" in result
        assert "https://jobs.example.com" in result

    def test_decodes_html_entities(self):
        result = strip_html("AT&amp;T &lt;hiring&gt;")
        assert "AT&T" in result
        assert "<hiring>" in result
        assert "&amp;" not in result

    def test_collapses_excess_newlines(self):
        result = strip_html("<p>a</p><p>b</p><p>c</p>")
        assert "\n\n\n" not in result

    def test_strips_unknown_tags(self):
        result = strip_html("<strong>bold</strong> <em>italic</em>")
        assert "<strong>" not in result
        assert "bold" in result
        assert "italic" in result


class TestParseCompany:
    def test_basic_pipe_format(self):
        assert parse_company("Acme AI | Engineer | Remote") == "Acme AI"

    def test_leading_whitespace_stripped(self):
        assert parse_company("  Acme AI  | Engineer") == "Acme AI"

    def test_no_pipe_returns_whole_first_line(self):
        assert parse_company("Acme AI — hiring engineers") == "Acme AI — hiring engineers"

    def test_empty_company_returns_unknown(self):
        assert parse_company(" | Engineer | Remote") == "Unknown"

    def test_multiline_uses_first_line(self):
        assert parse_company("Acme AI | Engineer\nFull description here") == "Acme AI"


class TestParseTitle:
    def test_extracts_second_segment(self):
        assert parse_title("Acme | Senior ML Engineer | Remote") == "Senior ML Engineer"

    def test_no_pipe_returns_none(self):
        assert parse_title("Acme AI hiring engineers") is None

    def test_empty_second_segment_returns_none(self):
        assert parse_title("Acme |  | Remote") is None

    def test_single_segment_returns_none(self):
        assert parse_title("Acme AI") is None


class TestParseLocation:
    def test_detects_remote_keyword(self):
        result = parse_location("Acme | Engineer | Remote (US)")
        assert result == "Remote (US)"

    def test_detects_city_name(self):
        result = parse_location("Acme | Engineer | San Francisco, CA")
        assert result == "San Francisco, CA"

    def test_detects_us_state_abbreviation(self):
        result = parse_location("Acme | Engineer | New York, NY")
        assert result is not None
        assert "NY" in result

    def test_no_location_returns_none(self):
        result = parse_location("Acme | Engineer | Competitive Salary")
        assert result is None

    def test_hybrid_detected(self):
        result = parse_location("Acme | Engineer | Hybrid (NYC office)")
        assert result is not None
        assert "Hybrid" in result

    def test_skips_company_segment(self):
        # Company name is "Remote Inc" — should not be returned as location
        # because only segments[1:] are checked
        result = parse_location("Remote Inc | Engineer | Competitive Pay")
        assert result is None or "Competitive" not in result
