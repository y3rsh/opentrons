// @flow
import * as React from 'react'

import type { Command } from './command-types'

export type CommandListProps = {|
  commands: Array<Command>,
|}

export function CommandList(props: CommandListProps): React.Node {
  const { commands } = props

  return (
    <ul>
      {commands.map(command => (
        <li key={command.command_id}>{command.command_type}</li>
      ))}
    </ul>
  )
}
