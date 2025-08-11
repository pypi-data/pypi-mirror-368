ZwergETL Engine
===================

ETL engine for ZwergETL framework.

A lightweight ETL engine that implements the same technique for building ETL pipelines
as implemented in CloverDX engine (former CloverETL).

ZwergETL framework uses modular design. This particular module
implements the ETL engine itself without any additional components that can actually
extract transform or load data. The engine defines base classes and implements
classes that are responsible for execution of an ETL *graph*.

Other ETL components (readers, writers, connections etc.) are implemented in separate packages
named `zwergetl-components-*`.
