# Dinheiro Claro — sistema de conteudo automatizado (pSEO)

Site estatico de financas pessoais, gerado automaticamente a partir de `data/topics.json`,
monetizado com anuncios que pagam em Bitcoin (A-ADS) e com doacao em BTC/Lightning.
100% estatico: hospeda no GitHub Pages, sem backend, sem banco de dados.

## Como funciona o sistema

```
data/topics.json   ->  generator.py  ->  pages/*.html + index.html + sitemap.xml
                                          |
                              GitHub Actions (build.yml) regenera e publica sozinho
```

1. Voce (ou eu) adiciona topicos em `data/topics.json`.
2. `python3 generator.py` gera as paginas, o index, o sitemap e o robots.
3. O workflow `.github/workflows/build.yml` roda o gerador a cada push e publica.

## Estrutura

```
data/topics.json           base de topicos (fonte da verdade do conteudo)
data/ads.txt               texto/iframe do bloco de anuncio
generator.py               gerador de site estatico (templates embutidos)
pages/                     paginas geradas (nao editar a mao)
index.html                 gerado
sitemap.xml, robots.txt    gerados
sobre/contato/privacidade/termos/apoie.html   paginas institucionais
assets/style.css           estilos
.github/workflows/build.yml  automacao de build/publicacao
```

## Publicar no GitHub Pages

1. Crie um repositorio (pode ser publico).
2. Envie tudo para a branch `main`.
3. Settings -> Pages -> branch `main`, pasta `/ (root)`.
4. O site fica em `https://SEU-USUARIO.github.io/SEU-REPO/`.
5. Edite `data/topics.json` com o `base_url` correto e rode o gerador (ou deixe a Action rodar).

## Ativar a monetizacao (A-ADS, paga em Bitcoin sem KYC)

1. Crie uma conta no A-ADS apenas com um endereco de carteira Bitcoin.
2. Gere um bloco de anuncio e copie o iframe.
3. Cole o iframe em `data/ads.txt`.
4. Rode `python3 generator.py` — o bloco entra em todas as paginas automaticamente.

## Receber na sua carteira

- `apoie.html` tem dois campos para preencher: endereco BTC on-chain e Lightning Address.
- Substitua `COLE-SEU-ENDERECO-BTC-AQUI` e `COLE-SEU-LIGHTNING-ADDRESS-AQUI`.
- Doacoes caem direto na sua carteira. O A-ADS paga em BTC na carteira tambem.

## Adicionar conteudo

1. Adicione um objeto em `topics` no `data/topics.json` (slug, title, keyword, category,
   description, intro, sections, faq).
2. Rode `python3 generator.py`.
3. Commit. A Action publica.

## Realidade estatistica (sem promessa)

Simulacao de Monte Carlo (100 mil cenarios, 12 meses) para este modelo:

| Cenario | Chance de US$ 0 | Chance >= US$ 300/mes | Chance >= US$ 1.000/mes |
|---|---|---|---|
| Execucao fraca | 75% | 19% | 11% |
| Execucao otimizada | 45% | 54% | 47% |

O fator decisivo e trafego (SEO), que nao e garantivel. O sistema automatiza tudo o que
e automatizavel: geracao, publicacao, exibicao de anuncio e recebimento. O que nao se
automatiza e fazer gente chegar — isso depende de conteudo ranquear no Google.

## Observacoes honestas

- Google leva de 3 a 6 meses para enviar trafego relevante.
- A-ADS paga pouco por impressao; a renda depende de volume.
- Receber cripto pode ter implicacoes fiscais no seu pais. Anonimato tecnico nao isenta obrigacoes legais.
- Nao existe renda passiva garantida. Este sistema reduz o trabalho continuo, nao elimina o risco.
