import * as React from 'react'
import { useTranslation } from 'react-i18next'
import { Link } from 'react-router-dom'

import {
  Flex,
  Icon,
  Text,
  DIRECTION_COLUMN,
  SIZE_1,
  SPACING_2,
  SPACING_3,
  JUSTIFY_SPACE_BETWEEN,
} from '@opentrons/components'

import { useCurrentProtocol } from '../../organisms/ProtocolUpload/hooks'
import { useIsProtocolRunning } from './hooks'

import type { DiscoveredRobot } from '../../redux/discovery/types'

type RobotStatusBannerProps = Pick<DiscoveredRobot, 'name' | 'local'>

export function RobotStatusBanner(props: RobotStatusBannerProps): JSX.Element {
  const { name, local } = props
  const { t } = useTranslation('devices_landing')

  const protocolRecord = useCurrentProtocol()

  const isProtocolRunning = useIsProtocolRunning()

  const RunningProtocolBanner = (): JSX.Element => (
    <Flex>
      <Text
        paddingRight={SPACING_2}
        data-testid={`RobotStatusBanner_${name}_running_${protocolRecord?.data.metadata.protocolName}`}
      >
        {`${t('running')} ${protocolRecord?.data.metadata.protocolName}`}
      </Text>
      {/* TODO: link to specific run page when built out */}
      <Link
        to={`/devices/${name}/protocol-runs/run`}
        id="RobotStatusBanner_goToRun"
      >
        {t('go_to_run')}
      </Link>
    </Flex>
  )

  return (
    <Flex flexDirection={DIRECTION_COLUMN}>
      {/* robot_model can be seen in the health response, but only for "connectable" robots.
  Probably best to leave as "OT-2" for now */}
      <Text id="RobotStatusBanner_robotModel">OT-2</Text>
      <Flex justifyContent={JUSTIFY_SPACE_BETWEEN}>
        <Flex paddingBottom={SPACING_3}>
          <Text
            as="span"
            marginRight={SPACING_3}
            id="RobotStatusBanner_robotName"
          >
            {name}
          </Text>
          <Icon
            // local boolean corresponds to a wired usb connection
            name={local ? 'usb' : 'wifi'}
            size={SIZE_1}
            marginRight={SPACING_2}
          />
        </Flex>
        {isProtocolRunning ? <RunningProtocolBanner /> : null}
      </Flex>
    </Flex>
  )
}
