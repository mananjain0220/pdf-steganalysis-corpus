"""Explicit registry, bounded process execution, and reproducible I/O helpers."""
import contextlib
import hashlib
import importlib
import json
import multiprocessing as mp
import os
from pathlib import Path
import time

METHOD_CLASSES = {
 'a0_steganography': ('methods.a0_steganography.a0_steganography', 'A0SteganographyMethod'),
 'tj_operator': ('methods.tj_operator.tj_operator', 'TJOperatorMethod'),
 'xref_steganography': ('methods.xref_steganography.xref_steganography', 'XrefSteganographyMethod'),
 'xmp_steganography': ('methods.xmp_steganography.xmp_steganography', 'XMPSteganographyMethod'),
 'operator_lsb': ('methods.operator_lsb.operator_lsb_adapter', 'OperatorLSBMethod'),
 'orphanstream_steganography': ('methods.orphanstream_steganography.orphanstream_steganography', 'OrphanstreamSteganographyMethod'),
 'ws_steganography': ('methods.ws_steganography.ws_steganography', 'WsSteganographyMethod'),
 'hybrid_steganography': ('methods.hybrid_steganography.hybrid_steganography', 'HybridSteganographyMethod'),
 'opsyn_steganography': ('methods.opsyn_steganography.opsyn_steganography', 'OpsynSteganographyMethod'),
 'numfmt_steganography': ('methods.numfmt_steganography.numfmt_steganography', 'NumfmtSteganographyMethod'),
 'whitetext_steganography': ('methods.whitetext_steganography.whitetext_steganography', 'WhitetextSteganographyMethod'),
}
KEYED = {'hybrid_steganography', 'orphanstream_steganography',
         'ws_steganography', 'numfmt_steganography', 'opsyn_steganography'}
SEED = 20260921

def sha(data):
    return hashlib.sha256(data).hexdigest()

def json_write(path, value):
    path = Path(path); path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + '.tmp')
    temporary.write_text(json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + '\n')
    temporary.replace(path)

def method(name):
    module, cls = METHOD_CLASSES[name]
    return getattr(importlib.import_module(module), cls)()

def _child(fn, task, conn):
    # Suppress method output: extracted payloads, local paths and exceptions are private.
    import logging
    logging.disable(logging.CRITICAL)
    with open(os.devnull, 'w') as sink, contextlib.redirect_stdout(sink), contextlib.redirect_stderr(sink):
        os.dup2(sink.fileno(), 1)
        os.dup2(sink.fileno(), 2)
        try:
            value = fn(task)
        except BaseException as exc:
            value = {'worker_status': 'error', 'error_type': type(exc).__name__}
    conn.send(value); conn.close()

def bounded_map(fn, tasks, cache, workers=4, timeout=60):
    """One killable process per document. Resume only exact task fingerprints."""
    cache = Path(cache); cache.mkdir(parents=True, exist_ok=True)
    ctx = mp.get_context('fork')
    pending, active, results = list(tasks), [], {}
    total = len(pending); completed = 0
    while pending or active:
        while pending and len(active) < workers:
            task = pending.pop(0)
            ident = task['job_id']
            fingerprint = sha(json.dumps(task,sort_keys=True).encode())
            path = cache / (ident + '.json')
            if path.exists():
                saved = json.loads(path.read_text())
                if saved.get('task_fingerprint') == fingerprint:
                    results[ident] = saved['result']; completed += 1
                    continue
            recv, send = ctx.Pipe(duplex=False)
            proc = ctx.Process(target=_child, args=(fn,task,send))
            proc.start(); send.close()
            active.append((proc,recv,task,fingerprint,path,time.monotonic()))
        for item in list(active):
            proc,recv,task,fingerprint,path,start = item
            result = None
            if recv.poll():
                try: result = recv.recv()
                except EOFError: result = {'worker_status':'crashed'}
            elif not proc.is_alive():
                # The child can finish between poll() and is_alive(). Drain
                # its final message before declaring a crash.
                if recv.poll(0.1):
                    try: result=recv.recv()
                    except EOFError: result={'worker_status':'crashed','exit_code':proc.exitcode}
                else: result = {'worker_status':'crashed','exit_code':proc.exitcode}
            elif time.monotonic()-start > timeout:
                result = {'worker_status':'timeout'}
            if result is not None:
                if proc.is_alive(): proc.terminate()
                proc.join(timeout=2)
                if proc.is_alive(): proc.kill(); proc.join()
                recv.close(); active.remove(item)
                json_write(path, {'task_fingerprint':fingerprint, 'result':result})
                results[task['job_id']] = result; completed += 1
                if completed % 100 == 0 or completed == total:
                    print(f'{cache.name}: {completed}/{total}', flush=True)
        if active: time.sleep(0.02)
    return results
