from __future__ import annotations

import os


def auto_worker_count(job_count: int, available_cpus: int | None = None) -> int:
    """Determina o numero de workers a partir da demanda (jobs pendentes) e da
    capacidade disponivel (nucleos de CPU), sem exigir um valor fixo informado
    pelo operador.

    Reproduz localmente o comportamento de um compute cluster com escalonamento
    automatico (min_instances=0, max_instances=capacidade): o numero de
    instancias ativas nunca excede a capacidade do cluster nem a quantidade de
    trabalho enfileirado.
    """
    if job_count <= 0:
        return 0

    capacity = available_cpus if available_cpus is not None else (os.cpu_count() or 1)
    capacity = max(1, capacity)

    return max(1, min(job_count, capacity))
