# Retail Management System

Retail store back office built on hand-written data structures, built for the Data Structures and Algorithms course at ESLSCA University.

## What it does
| Feature | Data structure |
|---|---|
| Product catalogue with fast lookup by ID | **AVL tree** (self-balancing, with rotations on insert and delete) |
| Checkout line | **Queue** |
| Refund of the last sale | **Stack** of transactions |
| Stock change history | **Linked list** |
| Customer interaction log (CRM) | **Linked list** |

On top of these it adds:
- **Inventory tools:** low-stock alerts, slow movers and suggested restock quantities
- **Sales reporting:** revenue totals and sales by hour
- **Customer profiles** and **product recommendations**, based on purchase history and overall popularity
- A **Tkinter GUI** (`retail_gui.py`) on top of the core system (`retailsystem.py`)

## Repository
| Path | Contents |
|---|---|
| `retailsystem.py` | Core system and data structures |
| `retail_gui.py` | Desktop interface |
| `docs/presentation.pptx` | Presentation |

## Run
```bash
python retail_gui.py
```
Uses only the Python standard library (3.10+).
