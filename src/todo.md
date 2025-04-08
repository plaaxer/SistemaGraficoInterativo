último commit:

- criado a lista de objetos na user interface para poder permitir deletions e (no futuro) modifications

- criado objectManagerUi para tal propósito

- ajuste dos botões para fins estéticos

- refatoracao da UI

- implementadas as deletions de objetos

- parsing de coordenadas agora leva em conta o tipo do objeto

- algumas outras coisas

commit 31-03-2025:

- implementadas funções de translação, escalonamento e rotação plenamente funcionais

- removida limitação de somente inteiros do parsing para permitir fatores de escalonamento menores que 1 para diminuir objetos

- corrigido problema de atualização de coordenadas de polígonos que aninhava listas

commit 06-04-2025:

- implementado sistema de coordenadas normalizado com centro no canto inferior esquerdo (vetores vão de (0, 0) a (1, 1))
- função update_specific_scn() é a responsável por 1) atualizar as coordenadas normalizadas de cada um dos objetos e 2) rotacionar os objetos de acordo com a inclinação da window
- rotacionamento da window no botão Rotacionar
- atualmente as coordenadas normalizadas de todos os objetos são atualizadas sempre que há modificações ou adição de algum. Deixar para otimizar utilizando clipping futuramente
- criado botões para importar e exportar objetos, além de estruturar a lógica por trás (FileLoader é responsável por carregar e armazenar arquivos, OBJHandler é responsável por fazer o processamento de transformar um objeto em .obj e vice-versa - o que ainda não feito)

commit 07-04-2025

- completado as conversões de .obj para importação e exportação

- adição de lógica para cores e nomes em .obj

- obs: .obj ainda em 2d, e ainda são necessárias algumas verificações de erro

- mudanças urgentes no front-end dos popups (bem feios)