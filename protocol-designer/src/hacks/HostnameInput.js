// @flow
import * as React from 'react'
import { Box, Text } from '@opentrons/components'

import type { StyleProps } from '@opentrons/components'

export type HostnameInputProps = {|
  hostname: string,
  setHostname: string => mixed,
  ...StyleProps,
|}

export function HostnameInput(props: HostnameInputProps): React.Node {
  const { hostname, setHostname, ...styleProps } = props
  const [inputValue, setInputValue] = React.useState('')

  const handleSubmit = (event: SyntheticInputEvent<>) => {
    event.preventDefault()
    setHostname(inputValue)
    setInputValue('')
  }

  return (
    <Box as="form" onSubmit={handleSubmit} {...styleProps}>
      <Text marginBottom="0.5rem">
        <strong>Current robot:</strong> {hostname}
      </Text>
      <input
        type="text"
        value={inputValue}
        placeholder="IP address or hostname"
        onChange={event => setInputValue(event.target.value)}
      />
      <button type="submit">Set hostname</button>
    </Box>
  )
}
