#!/usr/bin/env python3
import os, collections, types, json, traceback, pprint
import pytest
import wrapper

TEST_DIRECTORY = os.path.dirname(__file__)


def validate_rendering(blobs):
    return all("pos" in b and "texture" in b and "player" in b for b in blobs)


def frame2set(frame):
    return {
        (
            ("pos", tuple(blob["pos"])),
            ("texture", blob["texture"]),
            ("player", blob["player"]),
        )
        for blob in frame
    }


def sort_blob_set(blobs):
    return [dict(b) for b in sorted(blobs)]


def verify_replay(student_trace, reference_trace):
    assert len(student_trace) == len(reference_trace)
    for fid, (student, reference) in enumerate(zip(student_trace, reference_trace)):
        stustatus, stuframe = student
        refstatus, refframe = reference
        if not validate_rendering(stuframe):
            return "Invalid frame (contains a malformed blob):\n {}".format(
                pprint.pformat(stuframe)
            )
        stuset, refset = frame2set(stuframe), frame2set(refframe)
        if stuset != refset or stustatus != refstatus:
            lines = ["", "# Frame #{} diverges from reference.".format(fid)]
            extraneous, missing = stuset - refset, refset - stuset
            if stustatus != refstatus:
                lines.append(
                    "\n## Incorrect game status: {} (expected {})".format(
                        stustatus, refstatus
                    )
                )
            if missing:
                lines.append("\n## Missing from your rendering:")
                lines.append(pprint.pformat(sort_blob_set(missing)))
            if extraneous:
                lines.append("\n## Found in your rendering, but unexpected:")
                lines.append(pprint.pformat(sort_blob_set(extraneous)))
            return "\n".join(lines)


TRANSLATIONVECTOR_TEMPLATE = (
    "Unexpected result: expected translation vector {}, got {}, for rectangles {}, {}."
)
INTERSECTION_TEMPLATE = "Unexpected result: your implementation claims that {} {} {}."


def verify_intersection(result, reference):
    for (r1, r2, res), ref in zip(result, reference):
        if res != ref:
            verb = "intersects" if res else "does not intersect"
            return INTERSECTION_TEMPLATE.format(r1, verb, r2)


def verify_translation_vector(result, reference):
    for (r1, r2, res), ref in zip(result, reference):
        if isinstance(res, list):
            res = tuple(res)
        if isinstance(ref, list):
            ref = tuple(ref)
        if res != ref:
            return TRANSLATIONVECTOR_TEMPLATE.format(ref, res, r1, r2)


def verify(result, input_data, gold):
    restype, result = result

    if restype == "error":
        return False, "raised an error: {}".format(result)

    try:
        test_type = input_data.pop("type")
        verifn = {
            "replay": verify_replay,
            "intersection": verify_intersection,
            "translation_vector": verify_translation_vector,
        }[test_type]
        errmsg = verifn(result, gold)

        if errmsg is not None:
            return False, errmsg
        else:
            return True, "is correct. Hooray!"
    except:
        traceback.print_exc()
        return False, "crashed :(. Stack trace is printed above so you can debug."


def verify_case(cname):
    # read .in and .out files from cases
    with open(os.path.join("cases", f"{cname}.in"), "r") as f:
        indata = f.read()

    with open(os.path.join("cases", f"{cname}.out"), "r") as f:
        outdata = f.read()

    # first run the test
    result = wrapper.run_test(json.loads(indata))

    # then run the verifier
    vresult, vmsg = verify(result, json.loads(indata), json.loads(outdata))

    # if failure, alert the test system
    if not vresult:
        raise AssertionError(vmsg)


##################################################
##  Tests
##################################################


@pytest.mark.parametrize("testgroup", range(5))
def test_part_one_one(testgroup):
    for i in range(max(1, testgroup*5), min((testgroup+1)*5, 24)):
        verify_case(i)


@pytest.mark.parametrize("testnum", range(24, 28))
def test_jumps(testnum):
    verify_case(testnum)


@pytest.mark.parametrize("testnum", range(28, 30))
def test_fire(testnum):
    verify_case(testnum)


@pytest.mark.parametrize("testnum", range(30, 31))
def test_storm(testnum):
    verify_case(testnum)


@pytest.mark.parametrize("testnum", range(31, 32))
def test_bees(testnum):
    verify_case(testnum)


@pytest.mark.parametrize("testnum", range(32, 37))
def test_caterpillars(testnum):
    verify_case(testnum)


@pytest.mark.parametrize("testnum", range(37, 39))
def test_vehicles(testnum):
    verify_case(testnum)


@pytest.mark.parametrize("testnum", range(39, 40))
def test_peanuts(testnum):
    verify_case(testnum)


@pytest.mark.skip(reason="test for optional behavior")
@pytest.mark.parametrize("testnum", range(39, 40))
def test_fastcollide(testnum):
    verify_case(testnum)


if __name__ == "__main__":
    import sys

    res = pytest.main(["-k", " or ".join(sys.argv[1:]), "-v", __file__])
