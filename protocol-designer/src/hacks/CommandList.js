// @flow
import * as React from 'react'
import { css } from 'styled-components'
import { Text, C_BLACK, C_BLUE } from '@opentrons/components'

import type { Command } from './command-types'
import type { Highlight } from './ui-types'

export type CommandListProps = {|
  commands: Array<Command>,
  highlights: Array<Highlight>,
  onCommandClick: (commandId: string) => mixed,
|}

export function CommandList(props: CommandListProps): React.Node {
  const { commands, highlights, onCommandClick } = props

  return (
    <ul
      css={css`
        list-style: none;
        padding-left: 0;
      `}
    >
      {commands.map(command => {
        const { commandId } = command
        const color = highlights.some(h => h.commandId === commandId)
          ? C_BLUE
          : C_BLACK

        return (
          <li
            key={commandId}
            onClick={() => onCommandClick(commandId)}
            css={css`
              margin-bottom: 0.5rem;
              cursor: pointer;

              &:hover {
                text-decoration: underline;
              }
            `}
          >
            <Text color={color}>{commandId}</Text>
          </li>
        )
      })}
    </ul>
  )
}
