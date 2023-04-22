if decide_index == 'x':
                    index = (i, j)
                    dir = 'x'
                elif decide_index == 'y':
                    index = (j, i)
                    dir = 'y'
                elif decide_index == 'xy1':
                    index = (j, self.board.size + j - (i + 1))
                    dir = 'xy'
                elif decide_index == 'xy2':
                    index = (i + j + 1, j)
                    dir = 'xy'
                elif decide_index == '-xy1':
                    index = (j, i - j)
                    dir = '-xy'
                elif decide_index == '-xy2':
                    index = (i + j + 1, self.board.size - (j + 1))
                    dir = '-xy'