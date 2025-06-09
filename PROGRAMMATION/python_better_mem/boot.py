# boot.py - Configuration optimisée pour votre robot
import gc
import machine

# Configuration garbage collector dès le démarrage
gc.enable()
gc.threshold(gc.mem_free() // 4 + gc.mem_alloc())

# Désactiver le REPL sur UART si pas utilisé (économise ~2KB)
# Décommentez si vous n'utilisez pas la liaison série pour debug
# import os
# os.dupterm(None, 1)

# Configuration de fréquence CPU (optionnel - peut économiser énergie)
# machine.freq(240000000)  # 240MHz au lieu de 125MHz par défaut

print(f"Boot - Mémoire disponible: {gc.mem_free()}")
print(f"Boot - Seuil GC: {gc.threshold()}")

# Pré-compilation optionnelle des modules critiques
# (décommentez si vous voulez pré-compiler certains modules)
# import sys 
# sys.path.append('/flash/lib')

gc.collect()
print(f"Boot terminé - Mémoire: {gc.mem_free()}")