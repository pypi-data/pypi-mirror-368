=====
Usage
=====


.. code-block:: python

    import time

    from httpetcd import clients


    client = clients.get_wrapped_client(
        endpoints=["http://localhost:2379/"],
        namespace='ns1',
        timeout=100,
    )

    # KV locks
    lock = client.kvlock.acquire(key_name="my-lock", ttl=10)
    lock.refresh()
    print("Lock ttl: %d" % lock.ttl())
    print("Lock is alive: %s" % lock.alive())
    lock.release()
    print("Lock is alive (after release): %s" % lock.alive())

    client.kvlock.acquire(key_name="another/lock", ttl=10)
    lock = list(client.kvlock.list())[0]
    lock.release()

    # Lease & KV
    lease = client.lease.grant(ttl=5)
    client.kv.new(key_name="expiring-key", value="expiring-value", lease=lease)
    print("KV items: %r" % list(client.kv.items()))
    client.kv.new(key_name="my-key", value="my-value")
    print("KV items: %r" % list(client.kv.items()))
    time.sleep(6)
    print("KV items (after expire): %r" % list(client.kv.items()))
