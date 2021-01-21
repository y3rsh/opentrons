/* eslint-disable react/prop-types */
import * as React from 'react'
import axios from 'axios'

import {
  useQuery,
  useMutation,
  useQueryClient,
  QueryClient,
  QueryClientProvider,
} from 'react-query'

import { ReactQueryDevtools } from 'react-query/devtools'

const SESSIONS_CACHE_KEY = 'sessions'

const queryClient = new QueryClient()

export const HttpApiProvider = props => {
  return (
    <QueryClientProvider client={queryClient}>
      {props.children}
      <ReactQueryDevtools initialIsOpen={true} />
    </QueryClientProvider>
  )
}

export const useHttpClient = hostname => {
  return React.useMemo(() => {
    return axios.create({
      baseURL: `http://${hostname}:31950`,
      headers: { 'Opentrons-Version': 2 },
    })
  }, [hostname])
}

export const useProtocolSession = hostname => {
  const client = useHttpClient(hostname)
  const { data: sessions } = useQuery(SESSIONS_CACHE_KEY, () =>
    client.get('/sessions').then(response => response.data.data)
  )

  return sessions?.find(s => s.sessionType === 'liveProtocol')
}

export const useCreateProtocolSession = hostname => {
  const client = useHttpClient(hostname)
  const queryClient = useQueryClient()

  const { mutate: createProtocolSession } = useMutation(
    () => {
      return client
        .post('/sessions', { data: { sessionType: 'liveProtocol' } })
        .then(response => {
          const sessionId = response.data.data.id

          return client.post(`/sessions/${sessionId}/commands/execute`, {
            data: {
              command: 'equipment.loadInstrument',
              data: { pipetteName: 'p300_single', mount: 'right' },
            },
          })
        })
    },
    { onSuccess: () => queryClient.invalidateQueries(SESSIONS_CACHE_KEY) }
  )

  return createProtocolSession
}

export const useMoveToWell = hostname => {
  const client = useHttpClient(hostname)
  const queryClient = useQueryClient()
  const session = useProtocolSession(hostname)

  const { mutate: moveToWell } = useMutation(
    moveToWellParams => {
      const pipetteId = session.details.pipettes[0].pipetteId

      return client.post(`/sessions/${session.id}/commands/execute`, {
        data: {
          command: 'pipette.moveToWell',
          data: { ...moveToWellParams, pipetteId },
        },
      })
    },
    { onSuccess: () => queryClient.invalidateQueries(SESSIONS_CACHE_KEY) }
  )

  return moveToWell
}
