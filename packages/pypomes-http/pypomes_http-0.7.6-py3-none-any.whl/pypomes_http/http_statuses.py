from enum import IntEnum
from typing import Final, Literal


class HttpStatus(IntEnum):
    """
    Statuses and corresponding codes for HTTP operations.
    """
    # Informational responses
    CONTINUE = 100
    SWITCHING_PROTOCOLS = 101
    PROCESSING = 102
    EARLY_HINTS = 103
    # Successful responses
    OK = 200
    CREATED = 201
    ACCEPTED = 202
    NON_AUTHORITATIVE_INFORMATION = 203
    NO_CONTENT = 204
    RESET_CONTENT = 205
    PARTIAL_CONTENT = 206
    MULTI_STATUS = 207
    ALREADY_REPORTED = 208
    IM_USED = 226
    # Redirection messages
    MULTIPLE_CHOICES = 300
    MOVED_PERMANENTLY = 301
    FOUND = 302
    SEE_OTHER = 303
    NOT_MODIFIED = 304
    USE_PROXY = 304
    TEMPORARY_REDIRECT = 307
    PERMANENT_REDIRECT = 308
    # Client error responses
    BAD_REQUEST = 400
    UNAUTHORIZED = 401
    PAYMENT_REQUIRED = 402
    FORBIDDEN = 403
    NOT_FOUND = 404
    METHOD_NOT_ALLOWED = 405
    NOT_ACCEPTABLE = 406
    PROXY_AUTHENTICATION_REQUIRED = 407
    REQUEST_TIMEOUT = 408
    CONFLICT = 409
    GONE = 410
    LENGTH_REQUIRED = 411
    PRECONDITION_FAILED = 412
    PAYLOAD_TOO_LARGE = 413
    URI_TOO_LONG = 414
    UNSUPPORTED_MEDIA_TYPE = 415
    RANGE_NOT_SATISFIABLE = 416
    EXPECTATION_FAILED = 417
    I_AM_A_TEAPOT = 418
    MISDIRECTED_REQUEST = 421
    UNPROCESSABLE_CONTENT = 422
    LOCKED = 423
    FAILED_DEPENDENCY = 424
    TOO_EARLY = 425
    UPGRADE_REQUIRED = 426
    PRECONDITION_REQUIRED = 428
    TOO_MANY_REQUESTS = 429
    REQUEST_HEADER_FIELDS_TOO_LARGE = 431
    UNAVAILABLE_FOR_LEGAL_REASONS = 451
    # Server error responses
    INTERNAL_SERVER_ERROR = 500
    NOT_IMPLEMENTED = 501
    BAD_GATEWAY = 502
    SERVICE_UNAVAILABLE = 503
    GATEWAY_TIMEOUT = 504
    HTTP_VERSION_NOT_SUPPORTED = 505
    VARIANT_ALSO_NEGOTIATES = 506
    INSUFFICIENT_STORAGE = 507
    LOOP_DETECTED = 508
    NOT_EXTENDED = 510
    NETWORK_AUTHENTICATION_REQUIRED = 511


# https://developer.mozilla.org/en-US/docs/Web/HTTP/Status
# https://developer.mozilla.org/pt-BR/docs/Web/HTTP/Status

_HTTP_STATUSES: Final[dict] = {
    # Informational responses
    HttpStatus.CONTINUE: {  # 100
        "en": ("Interim response, indicating that the client should "
               "continue the request or ignore the response if the request is already finished."),
        "pt": ("Resposta provisória, indicando que o cliente deve continuar "
               "a solicitação ou ignorar a resposta se a solicitação já estiver concluída."),
    },
    HttpStatus.SWITCHING_PROTOCOLS: {  # 101
        "en": ("Sent in response to an upgrade request header from the client, "
               "indicating the protocol the server is switching to."),
        "pt": ("Enviado em resposta a um cabeçalho de solicitação Upgrade do cliente, "
               "indicando o protocolo para o qual o servidor está mudando."),
    },
    HttpStatus.PROCESSING: {  # 102
        "en": ("Indicates that the server has received and is processing the request, "
               "but no response is available yet."),
        "pt": ("Indica que o servidor recebeu e está processando a requisição, "
               "mas nenhuma resposta está disponível ainda."),
    },
    HttpStatus.EARLY_HINTS: {  # 103
        "en": ("Used with the 'Link' header, letting the user agent start "
               "preloading resources while the server prepares a response."),
        "pt": ("Usado com o cabeçalho 'Link', permitindo que o agente do usuário "
               "inicie o pré-carregamento de recursos enquanto o servidor prepara uma resposta."),
    },
    # Successful responses
    HttpStatus.OK: {  # 200
        "en": "The request succeeded.",
        "pt": "A solicitação foi bem-sucedida.",
    },
    HttpStatus.CREATED: {  # 201
        "en": "The request succeeded, and a new resource was created as a result.",
        "pt": "A requisição foi bem sucedida e um novo recurso foi criado como resultado.",
    },
    HttpStatus.ACCEPTED: {  # 202
        "en": "The request has been received but not yet acted upon.",
        "pt": "A solicitação foi recebida, mas ainda não foi atendida.",
    },
    HttpStatus.NON_AUTHORITATIVE_INFORMATION: {  # 203
        "en": ("The returned metadata is not exactly the same as is available from the origin server, "
               "but is collected from a local or a third-party copy."),
        "pt": ("Os metadados retornados não são exatamente os mesmos que estão disponíveis "
               "no servidor de origem, mas são coletados de uma cópia local ou de terceiros."),
    },
    HttpStatus.NO_CONTENT: {  # 204
        "en": "There is no content to send for this request, but the headers may be useful.",
        "pt": "Não há conteúdo para enviar para esta solicitação, mas os cabeçalhos podem ser úteis.",
    },
    HttpStatus.RESET_CONTENT: {  # 205
        "en": "Tells the user agent to reset the document which sent this request.",
        "pt": "Diz ao agente do usuário para redefinir o documento que enviou esta solicitação.",
    },
    HttpStatus.PARTIAL_CONTENT: {  # 206
        "en": "used when the 'Range' header is sent from the client to request only part of a resource.",
        "pt": "Usado quando o cabeçalho 'Range' é enviado do cliente para solicitar apenas parte de um recurso.",
    },
    HttpStatus.MULTI_STATUS: {  # 207
        "en": ("Conveys information about multiple resources, "
               "for situations where multiple status codes might be appropriate."),
        "pt": ("Transmite informações sobre vários recursos, "
               "para situações em que vários códigos de status podem ser apropriados."),
    },
    HttpStatus.ALREADY_REPORTED: {  # 208
        "en": "Used inside a '<dav:propstat>' response element to avoid "
              "repeatedly enumerating the internal members of multiple bindings to the same collection.",
        "pt": ("Usado dentro de um elemento de resposta '<dav:propstat>' para evitar "
               "enumerar repetidamente os membros internos de várias ligações para a mesma coleção."),
    },
    HttpStatus.IM_USED: {  # 226
        "en": ("The server has fulfilled a 'GET' request for the resource, and the response is a "
               "representation of the result of one or more instance-manipulations applied to the current instance."),
        "pt": ("O servidor atendeu a uma solicitação 'GET' para o recurso e a resposta é uma representação "
               "do resultado de uma ou mais manipulações de instância aplicadas à instância atual."),
    },
    # Redirection messages
    HttpStatus.MULTIPLE_CHOICES: {  # 300
        "en": ("The request has more than one possible response. "
               "The user agent or user should choose one of them."),
        "pt": ("A solicitação tem mais de uma resposta possível. "
               "O agente do usuário ou usuário deve escolher uma delas."),
    },
    HttpStatus.MOVED_PERMANENTLY: {  # 301
        "en": "The URL of the requested resource has been changed permanently. The new URL is given in the response.",
        "pt": "A URL do recurso solicitado foi permanentemente alterada. A nova URL é fornecida na resposta.",
    },
    HttpStatus.FOUND: {  # 302
        "en": ("The URI of requested resource has been changed temporarily. "
               "Further changes in the URI might be made in the future. "),
        "pt": ("A URI do recurso solicitado foi alterado temporariamente. "
               "Outras alterações na URI podem ser feitas no futuro."),
    },
    HttpStatus.SEE_OTHER: {  # 303
        "en": ("The server sent this response to direct the client to get "
               "the requested resource at another URI with a 'GET' request."),
        "pt": ("O servidor enviou esta resposta para direcionar o cliente "
               "a obter o recurso solicitado em outro URI com uma solicitação 'GET'."),
    },
    HttpStatus.NOT_MODIFIED: {  # 304
        "en": ("Tells the client that the response has not been modified, "
               "so the client can continue to use the same cached version of the response."),
        "pt": ("Informa ao cliente que a resposta não foi modificada; "
               "portanto, o cliente pode continuar a usar a mesma versão em cache da resposta."),
    },
    HttpStatus.USE_PROXY: {  # 305
        "en": ("Indicates that a requested response must be accessed by a proxy. "
               "It has been deprecated due to security concerns regarding in-band configuration of a proxy."),
        "pt": ("Indica que uma resposta solicitada deve ser acessada por um proxy. "
               "Foi descontinuado devido a questões de segurança em relação à configuração em banda de um proxy."),
    },
    HttpStatus.TEMPORARY_REDIRECT: {  # 307
        "en": ("The server sends this response to direct the client to get the "
               "requested resource at another URI, with the same method that was used in the prior request."),
        "pt": ("O servidor envia esta resposta para direcionar o cliente a obter "
               "o recurso solicitado em outra URI, com o mesmo método usado na solicitação anterior."),
    },
    HttpStatus.PERMANENT_REDIRECT: {  # 308
        "en": ("Indicates that the resource is now permanently located at another URI, "
               "specified by the 'Location:' HTTP Response header."),
        "pt": ("Indica que o recurso agora está permanentemente localizado em outra URI, "
               "especificada pelo cabeçalho de resposta HTTP 'Location:'."),
    },
    # Client error responses
    HttpStatus.BAD_REQUEST: {  # 400
        "en": ("The server cannot process the request due to something that is perceived to be a client error "
               "(e.g., malformed request syntax, invalid request message framing, or deceptive request routing)."),
        "pt": ("O servidor não pode processar a solicitação devido a algo que é percebido como um erro do cliente "
               "(e.g., solicitação malformada, roteamento ou enquadramento de mensagem de solicitação inválida)."),
    },
    HttpStatus.UNAUTHORIZED: {  # 401
        "en": ("Semantically, this response means 'unauthenticated'. "
               "The client must authenticate itself to get the requested response."),
        "pt": ("Semanticamente, essa resposta significa 'unauthenticated'. "
               "O cliente deve se autenticar para obter a resposta solicitada."),
    },
    HttpStatus.PAYMENT_REQUIRED: {  # 402
        "en": "This response code is reserved for future use; no standard exists.",
        "pt": "Este código de resposta está reservado para uso futuro; não existe convenção padrão.",
    },
    HttpStatus.FORBIDDEN: {  # 403
        "en": ("The client does not have access rights to the content. "
               "Unlike '401 Unauthorized', the client's identity is known to the server."),
        "pt": ("O cliente não tem direitos de acesso ao conteúdo. "
               "Ao contrário do '401 Unauthorized', a identidade do cliente é conhecida pelo servidor."),
    },
    HttpStatus.NOT_FOUND: {  # 404
        "en": ("The server cannot find the requested resource. Either the URL is not recognized, the resource "
               "does not exist, or the server is hiding the existence of a resource from an unauthorized client."),
        "pt": ("O servidor não pode encontrar o recurso solicitado. A URL não é reconhecida, o recurso não existe, "
               "ou o servidor está ocultando a existência de um recurso de um cliente não autorizado."),
    },
    HttpStatus.METHOD_NOT_ALLOWED: {  # 405
        "en": "The request method is known by the server but is not supported by the target resource. "
              "For example, an API may not allow calling 'DELETE' to remove a resource.",
        "pt": "O método de solicitação é conhecido pelo servidor, mas não é suportado pelo recurso de destino. "
              "Por exemplo, uma API pode não permitir chamar 'DELETE' para remover um recurso.",
    },
    HttpStatus.NOT_ACCEPTABLE: {  # 406
        "en": ("After performing server-driven content negotiation, the server "
               "does not find any content that conforms to the criteria given by the user agent."),
        "pt": ("Após realizar negociação de conteúdo, o servidor não encontra conteúdo "
               "que esteja em conformidade com os critérios fornecidos pelo o agente do usuário."),
    },
    HttpStatus.PROXY_AUTHENTICATION_REQUIRED: {  # 407
        "en": "Semelhante a '401 Unauthorized', mas a autenticação precisa ser feita por um proxy.",
        "pt": "This is similar to '401 Unauthorized' but the authentication needs to be done by a proxy.",
    },
    HttpStatus.REQUEST_TIMEOUT: {  # 408
        "en": ("This response is sent on an idle or unused connection "
               "by the server, whenever it feels the need to shut it down."),
        "pt": ("Esta resposta é enviada pelo servidor em uma conexão ociosa ou "
               "não utilizada, sempre que seu desligamento se fizer necessário."),
    },
    HttpStatus.CONFLICT: {  # 409
        "en": "This response is sent when a request conflicts with the current state of the server.",
        "pt": "Esta resposta é enviada quando uma requisição conflitar com o estado atual do servidor.",
    },
    HttpStatus.GONE: {  # 410
        "en": ("This response is sent when the requested content "
               "has been permanently deleted from server, with no forwarding address."),
        "pt": ("Esta resposta é enviada quando o conteúdo solicitado "
               "foi excluído permanentemente do servidor, sem endereço de encaminhamento."),
    },
    HttpStatus.LENGTH_REQUIRED: {  # 411
        "en": ("The server rejected the request because the 'Content-Length' "
               "header field is not defined, and the server requires it."),
        "pt": ("O servidor rejeitou a solicitação porque o campo de cabeçalho "
               "'Content-Length' não está definido, e o servidor o exige."),
    },
    HttpStatus.PRECONDITION_FAILED: {  # 412
        "en": "The client has indicated preconditions in its headers which the server does not meet.",
        "pt": "O cliente indicou nos seus cabeçalhos pré-condições que o servidor não atende.",
    },
    HttpStatus.PAYLOAD_TOO_LARGE: {  # 413
        "en": ("The request entity is larger than limits defined by server. "
               "The server might close the connection or return a 'Retry-After' header field."),
        "pt": ("A entidade requisição é maior do que os limites definidos pelo servidor. "
               "O servidor pode fechar a conexão ou retornar um campo de cabeçalho 'Retry-After'."),
    },
    HttpStatus.URI_TOO_LONG: {  # 414
        "en": "The URI requested by the client is longer than the server is willing to interpret.",
        "pt": "A URI solicitada pelo cliente é mais longa do que o servidor está disposto a interpretar.",
    },
    HttpStatus.UNSUPPORTED_MEDIA_TYPE: {  # 415
        "en": ("The media format of the requested data is not supported by the server, "
               "so the server is rejecting the request."),
        "pt": ("O formato de mídia dos dados requisitados não é suportado pelo servidor, "
               "que portanto está rejeitando a requisição."),
    },
    HttpStatus.RANGE_NOT_SATISFIABLE: {  # 416
        "en": ("The range specified by the 'Range' header field in the request cannot be fulfilled. "
               "It's possible that the range is outside the size of the target URI's data."),
        "pt": ("O intervalo especificado pelo campo de cabeçalho 'Range' na solicitação não pode ser atendido. "
               "É possível que o intervalo esteja fora do tamanho dos dados da URI de destino."),
    },
    HttpStatus.EXPECTATION_FAILED: {  # 417
        "en": "The expectation indicated by the 'Expect' request header field cannot be met by the server.",
        "pt": "A expectativa indicada pelo campo de cabeçalho 'Expect' não pode ser atendida pelo servidor.",
    },
    HttpStatus.I_AM_A_TEAPOT: {  # 418
        "en": ("The server refuses the attempt to brew coffee with a teapot. "
               "This was an April Fools joke from 1998, kept in the official standard by popular demand."),
        "pt": ("O servidor recusa a tentativa de coar café num bule de chá. "
               "Essa foi uma brincadeira de 1o. de Abril em 1998, mantida no padrão oficial por clamor popular."),
    },
    HttpStatus.MISDIRECTED_REQUEST: {  # 421
        "en": ("The request was directed at a server that is not able to produce a response. "
               "The server is not configured to produce responses for the combination "
               "of scheme and authority that are included in the request URI."),
        "pt": ("A requisição foi direcionada a um servidor inapto a produzir a resposta. "
               "O servidor não está configurado para produzir respostas para a combinação "
               "de esquema e autoridade inclusas na URI da requisição."),
    },
    HttpStatus.UNPROCESSABLE_CONTENT: {  # 422
        "en": "The request was well-formed but was unable to be followed, due to semantic errors.",
        "pt": "A solicitação foi bem formada, mas não pôde ser atendida devido a erros semânticos.",
    },
    HttpStatus.LOCKED: {  # 423
        "en": "The resource that is being accessed is locked.",
        "pt": "O recurso que está sendo acessado está bloqueado.",
    },
    HttpStatus.FAILED_DEPENDENCY: {  # 424
        "en": "The request failed due to failure of a previous request.",
        "pt": "A solicitação falhou devido à falha de uma solicitação anterior.",
    },
    HttpStatus.TOO_EARLY: {  # 425
        "en": "The server is unwilling to risk processing a request that might be replayed.",
        "pt": "O servidor não está disposto a correr o risco de processar uma solicitação que pode ser repetida.",
    },
    HttpStatus.UPGRADE_REQUIRED: {  # 426
        "en": ("The server refuses to perform the request using the current protocol, "
               "but might be willing to do so after the client upgrades to a different protocol. "
               "The server sends an 'Upgrade' header in this response to indicate the required protocol(s)."),
        "pt": "O servidor se recusa a executar a solicitação usando o protocolo atual, "
              "mas pode estar disposto a fazê-lo depois que o cliente atualizar para um protocolo diferente. "
              "O servidor envia um cabeçalho 'Upgrade' nessa resposta, para indicar os protocolos necessários.",
    },
    HttpStatus.PRECONDITION_REQUIRED: {  # 428
        "en": ("The origin server requires the request to be conditional. "
               "Intended to prevent the 'lost update' problem, where a client 'GET's a resource's state, "
               "modifies it, and 'PUT's it back to the server, when meanwhile a third party has modified "
               "the state on the server, leading to a conflict."),
        "pt": ("O servidor de origem exige que a solicitação seja condicional. "
               "Previne o problema da 'atualização perdida', onde um cliente obtem ('GET') "
               "o estado de um recurso, o modifica e o coloca ('PUT') de volta no servidor, "
               "quando entretanto um terceiro modificou o estado no servidor, levando a um conflito."),
    },
    HttpStatus.TOO_MANY_REQUESTS: {  # 429
        "en": "The user has sent too many requests in a given amount of time ('rate limiting').",
        "pt": "O usuário enviou muitas requisições num dado tempo ('limitação de taxa').",
    },
    HttpStatus.REQUEST_HEADER_FIELDS_TOO_LARGE: {  # 431
        "en": ("The server is unwilling to process the request because its header fields are too large. "
               "The request may be resubmitted after the reduction of the size of the request header fields."),
        "pt": ("O servidor recusa-se a processar a solicitação porque seus campos de cabeçalho são muito grandes. "
               "A solicitação pode ser reenviada após a redução o tamanho dos campos do cabeçalho da solicitação."),
    },
    HttpStatus.UNAVAILABLE_FOR_LEGAL_REASONS: {  # 451
        "en": ("The user agent requested a resource that cannot legally be provided, "
               "such as a web page censored by a government."),
        "pt": ("O agente do usuário solicitou um recurso que não pode ser fornecido legalmente, "
               "tal como uma página da Web censurada por um governo."),
    },
    # Server error responses
    HttpStatus.INTERNAL_SERVER_ERROR: {  # 500
        "en": "The server has encountered a situation it does not know how to handle.",
        "pt": "O servidor encontrou uma situação com a qual não sabe lidar.",
    },
    HttpStatus.NOT_IMPLEMENTED: {  # 501
        "en": "The request method is not supported by the server and cannot be handled. "
              "The only methods that servers are required to support are 'GET' and 'HEAD'.",
        "pt": "O método da requisição não é suportado pelo servidor e não pode ser manipulado. "
              "Os únicos métodos que servidores são obrigados a suportar são 'GET' e 'HEAD'.",
    },
    HttpStatus.BAD_GATEWAY: {  # 502
        "en": ("The server, while working as a gateway to get a response "
               "needed to handle the request, got an invalid response."),
        "pt": ("O servidor, enquanto trabalhava como um gateway para obter uma resposta "
               "necessária para lidar com a solicitação, obteve uma resposta inválida."),
    },
    HttpStatus.SERVICE_UNAVAILABLE: {  # 503
        "en": ("The server is not ready to handle the request. "
               "Common causes are a server that is down for maintenance or is overloaded."),
        "pt": ("O servidor não está pronto para manipular a requisição. "
               "Causas comuns são um servidor em manutenção ou sobrecarregado."),
    },
    HttpStatus.GATEWAY_TIMEOUT: {  # 504
        "en": "The server is acting as a gateway and cannot get a response in time.",
        "pt": "O servidor está atuando como um gateway e não consegue obter uma resposta a tempo.",
    },
    HttpStatus.HTTP_VERSION_NOT_SUPPORTED: {  # 505
        "en": "The HTTP version used in the request is not supported by the server.",
        "pt": "A versão HTTP usada na requisição não é suportada pelo servidor.",
    },
    HttpStatus.VARIANT_ALSO_NEGOTIATES: {  # 506
        "en": ("The chosen variant resource is configured to engage in transparent content negotiation itself, "
               "and is therefore not a proper end point in the negotiation process."),
        "pt": ("O recurso variante escolhido está configurado para se envolver em negociação "
               "de conteúdo transparente, e portanto, não é um 'endpoint' adequado no processo de negociação."),
    },
    HttpStatus.INSUFFICIENT_STORAGE: {  # 507
        "en": ("The method could not be performed on the resource, because the server "
               "is unable to store the representation needed to successfully complete the request."),
        "pt": ("O método não pôde ser executado no recurso porque o servidor "
               "não pode armazenar a representação necessária para concluir a solicitação com êxito."),
    },
    HttpStatus.LOOP_DETECTED: {  # 508
        "en": "The server detected an infinite loop while processing the request.",
        "pt": "O servidor detectou um loop infinito ao processar a solicitação.",
    },
    HttpStatus.NOT_EXTENDED: {  # 510
        "en": "Further extensions to the request are required for the server to fulfill it.",
        "pt": "Extensões adicionais à solicitação são necessárias para que o servidor a atenda.",
    },
    HttpStatus.NETWORK_AUTHENTICATION_REQUIRED: {  # 511
        "en": "Indicates that the client needs to authenticate to gain network access.",
        "pt": "Indica que o cliente precisa se autenticar para obter acesso à rede.",
    },
}


def http_status_description(http_status: HttpStatus,
                            lang: Literal["en", "pt"] = "en") -> str:
    """
    Return the description of the HTTP status *status_code*.

    :param http_status: the HTTP status
    :param lang: optional language (*en* or *pt* - defaults to *en*)
    :return: the corresponding HTTP status description, in the given language
    """
    item: dict = _HTTP_STATUSES.get(http_status)
    return (item or {"en": "Unknown status code", "pt": "Status desconhecido"}).get(lang)
