# Toronto Road Safety Dashboard

Um mapa web interativo analisando padrões de colisões de trânsito em Toronto em relação a semáforos, ciclovias, bairros e escolas  construído com **ArcGIS API for Python** e **ArcGIS API for JavaScript**.

🔗 **[Demo ao vivo](https://cleisonpaiva.github.io/toronto-road-safety-dashboard/)**
🇬🇧 [English Version](README.md)

---

## Visão geral

Esse projeto analisa ~120.000 registros de colisões de trânsito do Toronto Police Service (últimos 2 anos) sob quatro dimensões espaciais:

| Análise | Método | Distância de Buffer | Justificativa |
|---|---|---|---|
| Colisões × Semáforos | Buffer de ponto + spatial join | 50m | Faixa comum em estudos de segurança viária para proximidade de interseções |
| Colisões × Ciclovias | Buffer de linha + spatial join | 25m | Largura típica de via urbana em Toronto; evita falsos positivos de ruas paralelas |
| Colisões × Bairros | Join point-in-polygon | N/A | Bairros são fronteiras administrativas mutuamente exclusivas  sem necessidade de buffer |
| Colisões × Escolas | Buffer de ponto + spatial join | 150m | "Zona de segurança escolar" legalmente definida pela Highway Traffic Amendment Act de Ontário (Bill 90, 2016) |

O resultado é publicado como camadas GeoJSON, renderizadas num mapa construído com ArcGIS JS API puro, usando mapa base OpenStreetMap  evitando consumo de créditos do ArcGIS Online.

## Por que esse projeto existe

Sou desenvolvedor full-stack (PHP/Laravel, C#/.NET, React) me mudando para Toronto para trabalhar como GIS Developer. Esse projeto teve dois objetivos: aprender ArcGIS API for Python na prática, e produzir um artefato demonstrável e completo  de dado bruto de portal público até um mapa interativo publicado  para entrevistas técnicas.

## Descobertas metodológicas principais

1. **Correção do bounding box.** Um bounding box aproximado de Toronto estava descartando silenciosamente registros válidos em Scarborough (Morningside Heights, West Rouge). Causa raiz: o box foi estimado manualmente, não derivado dos dados. Correção: o envelope real foi calculado a partir dos próprios limites oficiais de 158 bairros.

2. **Divergência de fronteiras de bairro.** Um spatial join manual (point-in-polygon contra os limites atuais) foi comparado com o campo `NEIGHBOURHOOD_158` já existente no dataset de colisões. A concordância foi de apenas 83%. A investigação mostrou que a divergência se concentra em blocos específicos de pares de bairros, repetidos centenas de vezes  não ruído aleatório de borda  indicando que os dois datasets referenciam versões diferentes do esquema de fronteiras (fronteiras foram redesenhadas/subdivididas ao longo do tempo), não erro geométrico.

## Limitações conhecidas

- Os dados de colisão refletem uma janela fixa de 2 anos; os resultados não se atualizam automaticamente.
- O campo `NEIGHBOURHOOD_158` pré-existente diverge ~17% de um spatial join fresco contra os limites atuais  este projeto usa os limites recalculados como fonte de verdade.
- Distâncias de buffer são estimativas fundamentadas (ou, no caso de escolas, um valor legislado)  não derivadas de um estudo formal de engenharia de tráfego.
- Sem publicação no ArcGIS Online / Feature Layers  decisão deliberada para evitar consumo de créditos organizacionais.

## Autor

**Cleison Mendes Paiva**  [GitHub](https://github.com/CleisonPaiva) · [LinkedIn](https://www.linkedin.com/in/paiva-cleison)
