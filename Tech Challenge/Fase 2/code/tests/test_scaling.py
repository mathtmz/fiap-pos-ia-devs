from pcos_fase2.scaling import auto_worker_count


def test_auto_worker_count_bounded_by_available_cpus():
    assert auto_worker_count(job_count=10, available_cpus=4) == 4


def test_auto_worker_count_bounded_by_job_count():
    assert auto_worker_count(job_count=2, available_cpus=8) == 2


def test_auto_worker_count_has_floor_of_one():
    assert auto_worker_count(job_count=5, available_cpus=0) == 1


def test_auto_worker_count_returns_zero_when_no_jobs():
    assert auto_worker_count(job_count=0, available_cpus=8) == 0
