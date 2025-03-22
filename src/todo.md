- O parsing de coordenadas em utils por enquanto apenas aceita coordenadas do tipo x, y para criar pontos, assim não dá para criar retas ou polígonos, consertar isso.
#parsing aceita está aceitando mais pontos, mas ainda no formato <x0, y0, x1, y1, x2, y2>

- Implementar line e wireframe; line sendo composto por dois pontos e wireframe por N lines
#wireframe colocado como uma lista de pontos

- Adicionar demais botões à UI como o de mover um objeto e também uma lista que demonstra quais os objetos atuais criados

- Algumas outras paradas que nao to lembrando



algumas modificacoes importantes:

- diminui o tamanho do app (mantive 16:9) para 1600x900
- tamanho da viewport foi para 1034x582
- como o código está dinâmico, para retornar ao normal se quisermos é só trocar em constants.py
- apanhei pro tkinter tentando consertar o control panel e fazer ele expandir para a direita, no fim precisava de pack_propagate(False)
- parsing de coordenadas no modelo correto agora
- cada objeto tem um id único e um nome (nome tal que por enquanto o GUI não dá suporte para personalizar, então é sempre "objeto")
- criado metodo de translacao de viewport
- criado botões para mover a window pelo mundo usando a translacao de viewport
- também criado para zoom in e zoom out; mas por algum motivo não está funcionando e a janela está se movendo(?)