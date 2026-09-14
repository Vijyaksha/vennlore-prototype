"""Tests for ccslib — parsing the Chinese Chemical Society conference-paper
retrieval system (会议论文检索系统) at chemsoc.org.cn/library/papers/.

The system is a rung-4 deposit index: each meeting has a 论文集 table listing one
abstract volume (摘要集) per division, each with its own stated 论文数 count.
"""
import ccslib

LIST_PAGE = """
<table>
<tr><td>2024</td><td>中国化学会第34届学术年会</td><td>广东省广州市</td>
    <td><input type="button" onclick="location.href='meeting.php?id=296';"/></td></tr>
<tr><td>2023</td><td>中国化学会第33届学术年会</td><td>山东青岛</td>
    <td><input type="button" onclick="location.href='meeting.php?id=277';"/></td></tr>
</table>
<div>共找到210个会议 10个/页 第1/21页</div>
"""

MEETING_PAGE = """
<div>【会议名称】 中国化学会第34届学术年会</div>
<div>【会议时间】 2024年06月15日-18日</div>
<table>
<tr><td>名称</td><td>论文数</td><td>操作</td></tr>
<tr><td>中国化学会第34届学术年会摘要集-第1分会：表面物理化学</td><td>184</td><td></td></tr>
<tr><td>中国化学会第34届学术年会摘要集-第35分会：光化学</td><td>229</td><td></td></tr>
<tr><td>中国化学会第34届学术年会摘要集-大会特邀报告</td><td>3</td><td></td></tr>
</table>
"""


def test_meeting_list_yields_each_meeting_with_its_id():
    meetings = ccslib.parse_meeting_list(LIST_PAGE)

    assert meetings[0] == {"year": "2024", "name": "中国化学会第34届学术年会",
                           "place": "广东省广州市", "id": 296}
    assert meetings[1]["id"] == 277


def test_meeting_list_reports_how_many_meetings_the_system_holds():
    assert ccslib.parse_total_meetings(LIST_PAGE) == 210


def test_meeting_list_reports_the_page_count_so_the_crawl_knows_when_to_stop():
    assert ccslib.parse_page_count(LIST_PAGE) == 21


def test_volume_counts_are_read_off_the_paper_table():
    volumes = ccslib.parse_volumes(MEETING_PAGE)

    assert len(volumes) == 3
    assert volumes[0] == ("中国化学会第34届学术年会摘要集-第1分会：表面物理化学", 184)


def test_the_header_row_is_not_mistaken_for_a_volume():
    names = [n for n, _ in ccslib.parse_volumes(MEETING_PAGE)]

    assert "名称" not in names


def test_total_abstracts_sums_every_volume():
    assert ccslib.total_abstracts(MEETING_PAGE) == 184 + 229 + 3


def test_plenary_invited_volumes_are_reported_separately_so_they_can_be_excluded():
    """Rupert, 2026-09-12: invited speakers are NOT counted."""
    assert ccslib.invited_abstracts(MEETING_PAGE) == 3
    assert ccslib.contributed_abstracts(MEETING_PAGE) == 184 + 229


def test_meeting_name_is_read_off_the_record():
    assert ccslib.parse_meeting_name(MEETING_PAGE) == "中国化学会第34届学术年会"


def test_a_meeting_with_no_paper_table_counts_zero_rather_than_crashing():
    assert ccslib.total_abstracts("<html><body>no volumes here</body></html>") == 0
